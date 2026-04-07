#!/usr/bin/env python3
"""
Classificar Posts Criados — Stark Audiovisual

Lê JSONs do ClickUp de /tmp/posts_semana_*.json (salvos pela skill via MCP),
classifica tarefas por tipo (Carrossel, Estático, Capa/Reels para designers;
Vídeos, Capas, Patrocinados para editores), agrupa por membro/semana,
e escreve na planilha de Posts Criados.

Uso:
  python3 classificar_posts_criados.py                    # Processa e exibe
  python3 classificar_posts_criados.py --write             # Escreve na planilha
  python3 classificar_posts_criados.py --dry-run           # Apenas exibe, sem gravar
  python3 classificar_posts_criados.py --mes 3 --ano 2026  # Mês específico
"""

import json
import glob
import os
import sys
import re
import argparse
import unicodedata
from datetime import datetime, timedelta
from collections import defaultdict

# =====================================================================
# CONFIGURACAO
# =====================================================================

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

# Planilha de Posts Criados (Analise de Artes - AV)
POSTS_SHEET_ID = '1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I'

# =====================================================================
# CONSTANTES DO TIME
# =====================================================================

TEAM = {
    82154730:  'Humberto',
    112104835: 'João',
    84856123:  'Eloy',
    112104837: 'Max',
    106090854: 'Karyne',
    106172497: 'Milena',
    188585120: 'Ebertty',
    82029622:  'André',
    248549658: 'Mateus Redman',
}

# Nomes na planilha (primeiro nome → nome na planilha)
NOMES_PLANILHA = {
    'Eloy':          'Eloy Lopes',
    'Humberto':      'Humberto Salles',
    'Karyne':        'Karyne Torres',
    'Milena':        'Milena Carneiro',
    'João':          'João Andare',
    'Max':           'Max Miranda',
    'André':         'Andre Mello',
    'Ebertty':       'Ebertty Matnai',
    'Mateus Redman': 'Mateus Redmann',
}

DESIGNERS = ['Eloy', 'Humberto', 'Karyne', 'Milena', 'João', 'Max']
EDITORES = ['André', 'Ebertty', 'Mateus Redman']

MESES_PT = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]


# =====================================================================
# CLASSIFICACAO POR TIPO
# =====================================================================

def normalizar(texto):
    """Remove acentos e converte para uppercase."""
    texto = str(texto).strip()
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).upper()


def classificar_tipo_designer(task_name):
    """Classifica tipo de post de designer pelo nome da tarefa.

    Retorna: 'Carrossel', 'Estático' ou 'Capa/Reels'
    """
    nome = normalizar(task_name)

    # Capa/Reels: capas de reels, reels virais, 3D, etc.
    # IMPORTANTE: "Capa" sozinho no início = capa de reels (não estático)
    if re.search(r'\bCAPA\b', nome):
        return 'Capa/Reels'
    if re.search(r'\bREELS?\b', nome):
        return 'Capa/Reels'
    if re.search(r'\bVIRAL\b', nome):
        return 'Capa/Reels'
    if re.search(r'\b3D\b', nome):
        return 'Capa/Reels'
    if re.search(r'\bLIVE\b', nome):
        return 'Capa/Reels'

    # Estático
    if re.search(r'\bESTATICO\b', nome):
        return 'Estático'

    # Carrossel (padrão mais comum)
    if re.search(r'\bCARROSSEL\b', nome):
        return 'Carrossel'

    # Timing Post, Dia da mulher, etc. → Estático
    if re.search(r'\bTIMING\b', nome):
        return 'Estático'
    if re.search(r'\bDIA DA\b', nome) or re.search(r'\bDIA DAS\b', nome):
        return 'Estático'

    # Default: Carrossel (tipo mais comum para designers)
    return 'Carrossel'


def classificar_tipo_editor(task_name):
    """Classifica tipo de post de editor pelo nome da tarefa.

    Retorna: 'Vídeos Editados', 'Capas Editadas' ou 'Patrocinados'
    """
    nome = normalizar(task_name)

    # Patrocinados
    if re.search(r'\bPATROCINAD', nome):
        return 'Patrocinados'

    # Capas Editadas (capa de reels para editores)
    if re.search(r'\bCAPA\b', nome) and re.search(r'\bEDIC', nome):
        return 'Capas Editadas'
    if re.search(r'^CAPA\s*\|', nome):
        return 'Capas Editadas'
    if re.search(r'\bEDICAO DE CAPA\b', nome):
        return 'Capas Editadas'

    # Vídeos Editados (reels, edição de vídeo, etc.)
    if re.search(r'\bREELS?\b', nome):
        return 'Vídeos Editados'
    if re.search(r'\bVIDEO\b', nome):
        return 'Vídeos Editados'
    if re.search(r'\bEDICAO DE VIDEO\b', nome):
        return 'Vídeos Editados'
    if re.search(r'\bVIRAL\b', nome):
        return 'Vídeos Editados'
    if re.search(r'\b3D\b', nome):
        return 'Vídeos Editados'
    if re.search(r'\bLIVE\b', nome):
        return 'Vídeos Editados'

    # Default: Vídeos Editados (tipo mais comum para editores)
    return 'Vídeos Editados'


def extrair_semana_do_nome(task_name, semanas_config):
    """Extrai qual semana a tarefa pertence com base na data no nome.

    Procura por padrões DD/MM no nome da tarefa e compara com as semanas.
    Retorna: número da semana (1-5) ou None se não encontrar.
    """
    # Padrão: DD/MM no nome da tarefa
    match = re.search(r'(\d{1,2})/(\d{2})', task_name)
    if not match:
        return None

    dia = int(match.group(1))
    mes = int(match.group(2))

    for semana in semanas_config:
        seg = datetime.strptime(semana['segunda'], '%Y-%m-%d')
        dom = seg + timedelta(days=6)

        # Verificar se a data está na semana
        try:
            ano = seg.year
            data_task = datetime(ano, mes, dia)
            if seg <= data_task <= dom:
                return semana['week_num']
        except ValueError:
            continue

    return None


# =====================================================================
# CARREGAR DADOS
# =====================================================================

def carregar_tarefas_json():
    """Carrega tarefas de /tmp/posts_semana_*.json ou /tmp/clickup_filter_week*.json."""
    tarefas = {}

    # Tentar ambos os padrões de arquivo
    patterns = [
        '/tmp/posts_semana_*.json',
        '/tmp/clickup_filter_week*.json',
    ]

    files = []
    for pattern in patterns:
        files.extend(sorted(glob.glob(pattern)))

    if not files:
        print('ERRO: Nenhum arquivo de tarefas encontrado em /tmp/')
        print('Execute a skill /preencher-entrega-posts ou salve JSONs do ClickUp em /tmp/')
        sys.exit(1)

    for filepath in files:
        with open(filepath) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f'  Arquivo corrompido: {filepath}')
                continue

        # Extrair tarefas (vários formatos)
        tasks = []
        if isinstance(data, dict):
            tasks = data.get('tasks', data.get('results', data.get('items', [])))
        elif isinstance(data, list):
            tasks = data

        for task in tasks:
            tid = task.get('id')
            if tid and tid not in tarefas:
                tarefas[tid] = task

    print(f'Tarefas carregadas: {len(tarefas)} (de {len(files)} arquivos)')
    return tarefas


def gerar_config_semanas(mes, ano):
    """Gera configuração de semanas do mês."""
    semanas = []
    primeiro_dia = datetime(ano, mes, 1)

    # Encontrar primeira segunda-feira do mês
    weekday = primeiro_dia.weekday()  # 0=seg, 6=dom
    if weekday != 0:
        primeira_seg = primeiro_dia + timedelta(days=(7 - weekday) % 7)
    else:
        primeira_seg = primeiro_dia

    # Se primeira segunda é depois do dia 7, incluir semana anterior
    if primeira_seg.day > 7:
        primeira_seg = primeiro_dia - timedelta(days=weekday)

    seg = primeira_seg
    week_num = 1
    while seg.month == mes or (seg.month < mes and seg + timedelta(days=6) >= primeiro_dia):
        if seg.month == mes:
            domingo = seg + timedelta(days=6)
            semanas.append({
                'week_num': week_num,
                'segunda': seg.strftime('%Y-%m-%d'),
                'domingo': domingo.strftime('%Y-%m-%d'),
                'semana_str': f"{seg.strftime('%d/%m')} a {domingo.strftime('%d/%m')}",
                'semana_date': seg.strftime('%d/%m/%Y'),
            })
            week_num += 1
        seg += timedelta(days=7)
        if week_num > 6:
            break

    return semanas


# =====================================================================
# PROCESSAR
# =====================================================================

def processar_tarefas(tarefas, semanas_config):
    """Classifica tarefas por tipo e agrupa por membro/semana.

    Retorna:
    {
        'designers': {
            'João': {1: {'Carrossel': 15, 'Estático': 10, 'Capa/Reels': 5}, 2: ...},
            ...
        },
        'editores': {
            'André': {1: {'Vídeos Editados': 20, 'Capas Editadas': 15, 'Patrocinados': 0}, 2: ...},
            ...
        }
    }
    """
    designers = {nome: defaultdict(lambda: defaultdict(int)) for nome in DESIGNERS}
    editores = {nome: defaultdict(lambda: defaultdict(int)) for nome in EDITORES}

    tarefas_sem_semana = 0
    tarefas_sem_membro = 0
    tarefas_processadas = 0

    for tid, task in tarefas.items():
        task_name = task.get('name', '')

        # Extrair semana
        semana_num = extrair_semana_do_nome(task_name, semanas_config)
        if semana_num is None:
            tarefas_sem_semana += 1
            continue

        # Extrair assignees do time
        assignees = task.get('assignees', [])
        tem_membro = False

        for a in assignees:
            uid = a.get('id') or a.get('uid')
            try:
                uid = int(uid)
            except (ValueError, TypeError):
                continue

            nome = TEAM.get(uid)
            if not nome:
                continue

            tem_membro = True

            if nome in DESIGNERS:
                tipo = classificar_tipo_designer(task_name)
                designers[nome][semana_num][tipo] += 1
            elif nome in EDITORES:
                tipo = classificar_tipo_editor(task_name)
                editores[nome][semana_num][tipo] += 1

            tarefas_processadas += 1

        if not tem_membro:
            tarefas_sem_membro += 1

    print(f'Tarefas processadas: {tarefas_processadas}')
    print(f'Tarefas sem semana identificada: {tarefas_sem_semana}')
    print(f'Tarefas sem membro do time: {tarefas_sem_membro}')

    return {'designers': designers, 'editores': editores}


# =====================================================================
# EXIBIR RESULTADOS
# =====================================================================

def exibir_resultados(resultado, semanas_config):
    """Exibe tabela formatada dos resultados."""
    print('\n' + '=' * 80)
    print('POSTS CRIADOS — CLASSIFICAÇÃO POR TIPO')
    print('=' * 80)

    # Designers
    print('\n--- DESIGNERS ---')
    print(f'{"Nome":<18} {"Semana":<12} {"Carrossel":>10} {"Estático":>10} {"Capa/Reels":>11} {"Total":>6}')
    print('-' * 70)

    for nome in DESIGNERS:
        dados_nome = resultado['designers'][nome]
        total_nome = 0
        for semana in semanas_config:
            wn = semana['week_num']
            c = dados_nome[wn].get('Carrossel', 0)
            e = dados_nome[wn].get('Estático', 0)
            r = dados_nome[wn].get('Capa/Reels', 0)
            t = c + e + r
            total_nome += t
            if t > 0:
                print(f'{nome:<18} S{wn:<11} {c:>10} {e:>10} {r:>11} {t:>6}')
        if total_nome == 0:
            print(f'{nome:<18} {"(sem dados)":<12}')

    # Editores
    print('\n--- EDITORES ---')
    print(f'{"Nome":<18} {"Semana":<12} {"Vídeos":>10} {"Capas":>10} {"Patrocin.":>11} {"Total":>6}')
    print('-' * 70)

    for nome in EDITORES:
        dados_nome = resultado['editores'][nome]
        total_nome = 0
        for semana in semanas_config:
            wn = semana['week_num']
            v = dados_nome[wn].get('Vídeos Editados', 0)
            c = dados_nome[wn].get('Capas Editadas', 0)
            p = dados_nome[wn].get('Patrocinados', 0)
            t = v + c + p
            total_nome += t
            if t > 0:
                print(f'{nome:<18} S{wn:<11} {v:>10} {c:>10} {p:>11} {t:>6}')
        if total_nome == 0:
            print(f'{nome:<18} {"(sem dados)":<12}')


def comparar_com_planilha(resultado, semanas_config, client):
    """Compara dados do ClickUp com planilha existente e reporta divergências."""
    import gspread
    from google.oauth2.service_account import Credentials

    ss = client.open_by_key(POSTS_SHEET_ID)

    mes_str = MESES_PT[int(semanas_config[0]['segunda'].split('-')[1]) - 1]
    aba = None
    for ws in ss.worksheets():
        if normalizar(ws.title) == normalizar(mes_str):
            aba = ws
            break

    if not aba:
        print(f'\nAba {mes_str} não encontrada na planilha.')
        return {}

    dados = aba.get_all_values()
    divergencias = {}

    # Verificar designers (linhas 2+)
    for i, row in enumerate(dados[1:], start=2):
        if len(row) < 6:
            continue
        nome_str = str(row[1]).strip()
        total_str = str(row[5]).strip()

        # Identificar qual semana é esta linha
        semana_date = str(row[0]).strip()
        semana_num = None
        for s in semanas_config:
            if s.get('semana_date', '') == semana_date:
                semana_num = s['week_num']
                break
            # Também tentar match DD/MM/YYYY
            seg = datetime.strptime(s['segunda'], '%Y-%m-%d')
            if semana_date == seg.strftime('%d/%m/%Y'):
                semana_num = s['week_num']
                break

        if semana_num is None:
            continue

        # Encontrar nome do membro
        nome_membro = None
        nome_norm = normalizar(nome_str)
        for primeiro, planilha in NOMES_PLANILHA.items():
            if normalizar(planilha) == nome_norm or normalizar(primeiro) == nome_norm:
                nome_membro = primeiro
                break

        if not nome_membro or nome_membro not in DESIGNERS:
            continue

        # Comparar totais
        try:
            total_planilha = int(total_str) if total_str else 0
        except ValueError:
            total_planilha = 0

        dados_clickup = resultado['designers'][nome_membro][semana_num]
        total_clickup = sum(dados_clickup.values())

        if total_planilha > 0 and total_clickup > 0:
            diff = abs(total_clickup - total_planilha)
            if diff > 5:
                key = f'{nome_membro}_S{semana_num}'
                divergencias[key] = {
                    'nome': nome_membro,
                    'semana': semana_num,
                    'planilha': total_planilha,
                    'clickup': total_clickup,
                    'diff': diff,
                }

    if divergencias:
        print(f'\n*** DIVERGÊNCIAS ENCONTRADAS ({len(divergencias)}) ***')
        for key, d in divergencias.items():
            print(f'  {d["nome"]} S{d["semana"]}: Planilha={d["planilha"]} vs ClickUp={d["clickup"]} (diff={d["diff"]})')
    else:
        print('\nSem divergências significativas (diff <= 5).')

    return divergencias


# =====================================================================
# ESCREVER NA PLANILHA
# =====================================================================

def escrever_posts_criados(resultado, semanas_config, client, semanas_alvo=None):
    """Escreve dados classificados na planilha de Posts Criados.

    Args:
        resultado: dict com 'designers' e 'editores'
        semanas_config: lista de semanas do mês
        client: gspread client autenticado
        semanas_alvo: lista de week_nums para escrever (None = todas com dados)
    """
    import gspread

    ss = client.open_by_key(POSTS_SHEET_ID)
    mes_num = int(semanas_config[0]['segunda'].split('-')[1])
    mes_str = MESES_PT[mes_num - 1]

    aba = None
    for ws in ss.worksheets():
        if normalizar(ws.title) == normalizar(mes_str):
            aba = ws
            break

    if not aba:
        print(f'ERRO: Aba {mes_str} não encontrada.')
        return False

    print(f'\nEscrevendo na aba "{aba.title}"...')
    dados = aba.get_all_values()

    updates = []

    # Mapear linhas da planilha: {(semana_date, nome_planilha): row_index}
    mapa_linhas = {}
    for i, row in enumerate(dados):
        if len(row) < 6:
            continue
        semana_date = str(row[0]).strip()
        nome_str = str(row[1]).strip()
        mapa_linhas[(semana_date, normalizar(nome_str))] = i

    for semana in semanas_config:
        wn = semana['week_num']

        if semanas_alvo and wn not in semanas_alvo:
            continue

        seg = datetime.strptime(semana['segunda'], '%Y-%m-%d')
        semana_date = seg.strftime('%d/%m/%Y')

        # Designers
        for nome in DESIGNERS:
            dados_nome = resultado['designers'][nome][wn]
            c = dados_nome.get('Carrossel', 0)
            e = dados_nome.get('Estático', 0)
            r = dados_nome.get('Capa/Reels', 0)
            total = c + e + r

            if total == 0:
                continue

            nome_pl = NOMES_PLANILHA.get(nome, nome)
            key = (semana_date, normalizar(nome_pl))

            if key not in mapa_linhas:
                print(f'  AVISO: Linha não encontrada para {nome} S{wn} ({semana_date})')
                continue

            row_idx = mapa_linhas[key]  # 0-indexed
            row_num = row_idx + 1  # 1-indexed para gspread

            # Col C=Carrossel, D=Estático, E=Capa/Reels, F=Total
            updates.append({'range': f'C{row_num}', 'values': [[c]]})
            updates.append({'range': f'D{row_num}', 'values': [[e]]})
            updates.append({'range': f'E{row_num}', 'values': [[r]]})
            updates.append({'range': f'F{row_num}', 'values': [[total]]})

        # Editores
        for nome in EDITORES:
            dados_nome = resultado['editores'][nome][wn]
            v = dados_nome.get('Vídeos Editados', 0)
            cap = dados_nome.get('Capas Editadas', 0)
            p = dados_nome.get('Patrocinados', 0)
            total = v + cap + p

            if total == 0:
                continue

            nome_pl = NOMES_PLANILHA.get(nome, nome)
            key = (semana_date, normalizar(nome_pl))

            if key not in mapa_linhas:
                print(f'  AVISO: Linha não encontrada para {nome} S{wn} ({semana_date})')
                continue

            row_idx = mapa_linhas[key]
            row_num = row_idx + 1

            # Col C=Vídeos, D=Capas, E=Patrocinados, F=Total
            updates.append({'range': f'C{row_num}', 'values': [[v]]})
            updates.append({'range': f'D{row_num}', 'values': [[cap]]})
            updates.append({'range': f'E{row_num}', 'values': [[p]]})
            updates.append({'range': f'F{row_num}', 'values': [[total]]})

    if updates:
        aba.batch_update(updates)
        print(f'Sucesso! {len(updates) // 4} linhas atualizadas ({len(updates)} células).')
    else:
        print('Nenhuma atualização necessária.')

    # Atualizar resumo do lado direito
    _atualizar_resumo(resultado, semanas_config, aba, dados)

    return True


def _atualizar_resumo(resultado, semanas_config, aba, dados):
    """Atualiza o resumo do lado direito da planilha (totais por pessoa)."""
    import gspread

    updates = []

    # Calcular totais por designer
    totais_designers = {}
    totais_tipo_designer = {'Carrossel': 0, 'Estático': 0, 'Capa/Reels': 0}

    for nome in DESIGNERS:
        total = 0
        for semana in semanas_config:
            wn = semana['week_num']
            dados_nome = resultado['designers'][nome][wn]
            for tipo, qtd in dados_nome.items():
                total += qtd
                if tipo in totais_tipo_designer:
                    totais_tipo_designer[tipo] += qtd
        totais_designers[nome] = total

    # Calcular totais por editor
    totais_editores = {}
    totais_tipo_editor = {'Vídeos Editados': 0, 'Capas Editadas': 0, 'Patrocinados': 0}

    for nome in EDITORES:
        total = 0
        for semana in semanas_config:
            wn = semana['week_num']
            dados_nome = resultado['editores'][nome][wn]
            for tipo, qtd in dados_nome.items():
                total += qtd
                if tipo in totais_tipo_editor:
                    totais_tipo_editor[tipo] += qtd
        totais_editores[nome] = total

    # L2 H-K: Totais gerais designers
    total_geral_designers = sum(totais_designers.values())
    updates.append({'range': 'H2', 'values': [[totais_tipo_designer['Carrossel']]]})
    updates.append({'range': 'I2', 'values': [[totais_tipo_designer['Estático']]]})
    updates.append({'range': 'J2', 'values': [[totais_tipo_designer['Capa/Reels']]]})
    updates.append({'range': 'K2', 'values': [[total_geral_designers]]})

    # L4-5 H-L: Nomes + totais por designer (ordem da planilha)
    # A planilha já tem os nomes na L4 (H-L), totais na L5 (H-L)
    # Ordem: Eloy, João, Humberto, Karyne, Milena (+ Max se couber)
    # Vamos ler a L4 para saber a ordem
    if len(dados) > 3:
        ordem_designers = []
        for j in range(7, min(len(dados[3]), 13)):  # L4, cols H-L (idx 7-12)
            nome_cell = str(dados[3][j]).strip()
            nome_norm = normalizar(nome_cell)
            for primeiro, planilha in NOMES_PLANILHA.items():
                if normalizar(planilha) == nome_norm and primeiro in DESIGNERS:
                    ordem_designers.append((j, primeiro))
                    break

        if ordem_designers:
            for col_idx, nome in ordem_designers:
                col_letter = chr(ord('A') + col_idx)
                updates.append({'range': f'{col_letter}5', 'values': [[totais_designers.get(nome, 0)]]})

    # L7 H-K: Totais gerais editores
    total_geral_editores = sum(totais_editores.values())
    updates.append({'range': 'H7', 'values': [[totais_tipo_editor['Vídeos Editados']]]})
    updates.append({'range': 'I7', 'values': [[totais_tipo_editor['Capas Editadas']]]})
    updates.append({'range': 'J7', 'values': [[totais_tipo_editor['Patrocinados']]]})
    updates.append({'range': 'K7', 'values': [[total_geral_editores]]})

    # L10-11 H-J: Nomes + totais por editor
    if len(dados) > 9:
        ordem_editores = []
        for j in range(7, min(len(dados[9]), 11)):  # L10, cols H-J (idx 7-9)
            nome_cell = str(dados[9][j]).strip()
            nome_norm = normalizar(nome_cell)
            for primeiro, planilha in NOMES_PLANILHA.items():
                if normalizar(planilha) == nome_norm and primeiro in EDITORES:
                    ordem_editores.append((j, primeiro))
                    break

        if ordem_editores:
            for col_idx, nome in ordem_editores:
                col_letter = chr(ord('A') + col_idx)
                updates.append({'range': f'{col_letter}11', 'values': [[totais_editores.get(nome, 0)]]})

    if updates:
        aba.batch_update(updates)
        print(f'Resumo atualizado: {len(updates)} células.')


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='Classificar Posts Criados - Stark AV')
    parser.add_argument('--mes', type=int, help='Número do mês (1-12)')
    parser.add_argument('--ano', type=int, help='Ano')
    parser.add_argument('--write', action='store_true', help='Escrever na planilha')
    parser.add_argument('--dry-run', action='store_true', help='Apenas exibir, sem gravar')
    parser.add_argument('--semanas', help='Semanas a escrever (ex: "1,4" para S1 e S4)')
    parser.add_argument('--input', help='JSON com tarefas pré-processadas')
    args = parser.parse_args()

    hoje = datetime.now()
    mes = args.mes or hoje.month
    ano = args.ano or hoje.year

    print('=== CLASSIFICAR POSTS CRIADOS ===')
    print(f'Mês: {MESES_PT[mes - 1]} {ano}\n')

    # Gerar config de semanas
    semanas_config = gerar_config_semanas(mes, ano)
    print(f'Semanas do mês: {len(semanas_config)}')
    for s in semanas_config:
        print(f'  S{s["week_num"]}: {s["semana_str"]} (segunda: {s["segunda"]})')

    # Carregar tarefas
    if args.input:
        with open(args.input) as f:
            tarefas_raw = json.load(f)
        # Se for um dict de tasks por id
        if isinstance(tarefas_raw, dict) and not tarefas_raw.get('tasks'):
            tarefas = tarefas_raw
        else:
            tasks_list = tarefas_raw.get('tasks', tarefas_raw) if isinstance(tarefas_raw, dict) else tarefas_raw
            tarefas = {t['id']: t for t in tasks_list if 'id' in t}
        print(f'Tarefas carregadas do input: {len(tarefas)}')
    else:
        tarefas = carregar_tarefas_json()

    if not tarefas:
        print('\nNenhuma tarefa encontrada.')
        sys.exit(1)

    # Processar
    print()
    resultado = processar_tarefas(tarefas, semanas_config)

    # Exibir
    exibir_resultados(resultado, semanas_config)

    # Semanas alvo
    semanas_alvo = None
    if args.semanas:
        semanas_alvo = [int(s.strip()) for s in args.semanas.split(',')]
        print(f'\nSemanas alvo para escrita: {semanas_alvo}')

    if args.write and not args.dry_run:
        try:
            from google.oauth2.service_account import Credentials
            import gspread

            creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
            client = gspread.authorize(creds)
        except Exception as e:
            print(f'\nErro ao autenticar: {e}')
            sys.exit(1)

        # Verificar divergências em semanas já preenchidas
        print('\nVerificando divergências com planilha existente...')
        divergencias = comparar_com_planilha(resultado, semanas_config, client)

        # Escrever
        escrever_posts_criados(resultado, semanas_config, client, semanas_alvo)
        print(f'\nPlanilha: https://docs.google.com/spreadsheets/d/{POSTS_SHEET_ID}')
    elif args.dry_run:
        print('\n(Dry-Run) Não escrevendo na planilha.')

    # Salvar resultado como JSON
    output = {
        'mes': MESES_PT[mes - 1],
        'ano': ano,
        'semanas': [],
    }
    for semana in semanas_config:
        wn = semana['week_num']
        sem_data = {
            'week_num': wn,
            'semana_str': semana['semana_str'],
            'designers': {},
            'editores': {},
        }
        for nome in DESIGNERS:
            d = resultado['designers'][nome][wn]
            sem_data['designers'][nome] = dict(d) if d else {}
        for nome in EDITORES:
            d = resultado['editores'][nome][wn]
            sem_data['editores'][nome] = dict(d) if d else {}
        output['semanas'].append(sem_data)

    output_path = '/tmp/posts_criados_classificados.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f'\nResultado salvo em {output_path}')


if __name__ == '__main__':
    main()
