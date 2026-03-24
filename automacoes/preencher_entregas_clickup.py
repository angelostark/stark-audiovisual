#!/usr/bin/env python3
"""
Preencher Entrega de Posts — Stark Audiovisual

Lê JSONs do ClickUp de /tmp/clickup_raw_*.json (salvos pela skill via MCP),
salva dados brutos no Google Sheets, calcula % de entrega no prazo por
colaborador, e atualiza a planilha de entregas.

Uso:
  python3 preencher_entregas_clickup.py
  python3 preencher_entregas_clickup.py --dry-run
  python3 preencher_entregas_clickup.py --semana "16/03 a 22/03" --quarta 2026-03-18
"""

import json
import glob
import os
import sys
import argparse
import gspread
from datetime import datetime, time, timedelta
from google.oauth2.service_account import Credentials
import unicodedata

# =====================================================================
# CONFIGURACAO
# =====================================================================

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

# Planilha unica (dados brutos + entregas)
SHEET_ID = '1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA'

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

NOMES = {
    'Eloy':          'Eloy Lopes',
    'Humberto':      'Humberto Salles',
    'Karyne':        'Karyne Torres',
    'Milena':        'Milena Carneiro',
    'João':          'João',
    'Max':           'Max',
    'André':         'Andre Mello',
    'Ebertty':       'Ebertty Matnai',
    'Mateus Redman': 'Mateus Redmann',
}

STATUS_ENTREGUE = [
    'done', 'closed', 'edição concluída', 'aguardando postagem',
    'concluído', 'concluída', 'encerramento da tarefa', 'aprovado',
    'arte aprovada', 'finalizado',
]

META = 97.0

MESES_PT = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

EDITORES = ['André', 'Ebertty', 'Mateus Redman']


# =====================================================================
# UTILITARIOS
# =====================================================================

def normalizar(texto):
    texto = str(texto).strip()
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).upper()


def match_nome(texto):
    norm = normalizar(texto)
    for primeiro_nome, completo in NOMES.items():
        if normalizar(primeiro_nome) in norm or normalizar(completo) in norm:
            return primeiro_nome
    return None


# =====================================================================
# CARREGAR TAREFAS DOS JSONS LOCAIS
# =====================================================================

def carregar_tarefas_json(config):
    """Carrega e filtra tarefas dos arquivos /tmp/clickup_raw_*.json"""
    dias = config['dias']
    tarefas = {}

    for filepath in sorted(glob.glob('/tmp/clickup_raw_*.json')):
        with open(filepath) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f'  Arquivo corrompido, ignorando: {filepath}')
                continue

        # Extrair resultados (formato do MCP clickup_search)
        items = []
        if isinstance(data, dict):
            if 'results' in data:
                items = data['results']
            elif 'items' in data:
                items = data['items']
            elif 'tasks' in data:
                items = data['tasks']
            elif 'id' in data:
                items = [data]
        elif isinstance(data, list):
            items = data

        for task in items:
            tid = task.get('id')
            if tid:
                tarefas[tid] = task

    print(f'Tarefas brutas carregadas: {len(tarefas)}')

    # Filtrar: subtasks, dias da semana, assignees do time
    filtradas = {}
    for tid, task in tarefas.items():
        # Deve ser subtask
        hierarchy = task.get('hierarchy', {})
        if not hierarchy.get('task'):
            continue

        # Deve ter hasNameMatch ou conter dia no nome
        search_ctx = task.get('searchContext', {})
        has_name_match = search_ctx.get('hasNameMatch', False)

        name = task.get('name', '')
        parent_task = hierarchy.get('task', {})
        parent_name = parent_task.get('name', '') if isinstance(parent_task, dict) else ''

        dia_encontrado = has_name_match
        if not dia_encontrado:
            for dia in dias:
                if dia in name or dia in parent_name:
                    dia_encontrado = True
                    break

        if not dia_encontrado:
            continue

        # Deve ter assignee do time
        assignees = task.get('assignees', [])
        tem_membro = False
        for a in assignees:
            uid = a.get('id') or a.get('uid')
            try:
                if int(uid) in TEAM:
                    tem_membro = True
                    break
            except (ValueError, TypeError):
                pass

        if not tem_membro:
            continue

        filtradas[tid] = task

    print(f'Tarefas filtradas da semana: {len(filtradas)}')
    return filtradas


# =====================================================================
# SALVAR DADOS BRUTOS NO GOOGLE SHEETS
# =====================================================================

def salvar_dados_brutos(client, tarefas, semana_str):
    """Limpa e grava dados brutos na aba 'Dados Brutos'."""
    ss = client.open_by_key(SHEET_ID)
    aba = ss.worksheet('Dados Brutos')

    # Limpar dados antigos (manter header)
    aba.batch_clear(['A2:J'])

    if not tarefas:
        print('Nenhuma tarefa para gravar nos dados brutos.')
        return

    # Montar linhas
    linhas = []
    for tid, task in tarefas.items():
        status_raw = task.get('status', '')
        if isinstance(status_raw, dict):
            status_str = status_raw.get('status', '')
        else:
            status_str = str(status_raw)

        date_updated = task.get('dateUpdated', '') or task.get('date_updated', '')

        hierarchy = task.get('hierarchy', {})
        parent_task = hierarchy.get('task', {})
        parent_name = parent_task.get('name', '') if isinstance(parent_task, dict) else ''

        list_info = hierarchy.get('subcategory', {})
        list_id = list_info.get('id', '') if isinstance(list_info, dict) else ''

        date_created = task.get('dateCreated', '') or task.get('date_created', '')

        for assignee in task.get('assignees', []):
            uid = assignee.get('id') or assignee.get('uid') or ''
            username = assignee.get('username', '')

            try:
                if int(uid) not in TEAM:
                    continue
            except (ValueError, TypeError):
                continue

            linhas.append([
                semana_str,
                tid,
                task.get('name', ''),
                status_str.lower().strip(),
                str(date_updated),
                str(uid),
                username,
                parent_name,
                str(list_id),
                str(date_created),
            ])

    if linhas:
        aba.update(f'A2:J{len(linhas) + 1}', linhas)
        print(f'Dados brutos: {len(linhas)} linhas gravadas na aba "Dados Brutos".')


def atualizar_status(client, tasks_count, status='OK', error=''):
    """Atualiza aba 'Status' com resultado da execução."""
    ss = client.open_by_key(SHEET_ID)
    try:
        aba = ss.worksheet('Status')
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        aba.update('A2:D2', [[now_str, status, str(tasks_count), error]])
    except Exception:
        pass  # Status é opcional


# =====================================================================
# CALCULAR ENTREGAS
# =====================================================================

def calcular_entregas(tarefas, prazo_ms):
    """Calcula demandas e entregas no prazo por colaborador."""
    demandas = {name: 0 for name in TEAM.values()}
    entregues = {name: 0 for name in TEAM.values()}

    for tid, task in tarefas.items():
        status_raw = task.get('status', '')
        if isinstance(status_raw, dict):
            status_str = status_raw.get('status', '').lower().strip()
        else:
            status_str = str(status_raw).lower().strip()

        is_entregue = status_str in STATUS_ENTREGUE

        date_updated_ms = None
        du = task.get('dateUpdated') or task.get('date_updated')
        if du:
            try:
                date_updated_ms = int(du)
            except (ValueError, TypeError):
                pass

        entregue_no_prazo = False
        if is_entregue:
            if date_updated_ms is not None:
                entregue_no_prazo = date_updated_ms <= prazo_ms
            else:
                entregue_no_prazo = True

        for assignee in task.get('assignees', []):
            uid = assignee.get('id') or assignee.get('uid')
            try:
                uid = int(uid)
            except (ValueError, TypeError):
                continue
            nome = TEAM.get(uid)
            if not nome:
                continue

            demandas[nome] += 1
            if entregue_no_prazo:
                entregues[nome] += 1

    return demandas, entregues


# =====================================================================
# ESCREVER NA PLANILHA DE ENTREGAS
# =====================================================================

def _semana_match(cell_value, semana_str, segunda_date_str):
    """Verifica se o valor da celula corresponde a semana.

    Aceita formatos: "16/03/2026", "16/03 a 22/03", "16/03", etc.
    segunda_date_str: "2026-03-16" (YYYY-MM-DD)
    """
    cell = str(cell_value).strip()
    if not cell:
        return False
    # Match direto com semana_str (ex: "16/03 a 22/03")
    if semana_str.lower() in cell.lower():
        return True
    # Extrair DD/MM da segunda-feira
    if segunda_date_str:
        try:
            dt = datetime.strptime(segunda_date_str, '%Y-%m-%d')
            dd_mm = dt.strftime('%d/%m')
            dd_mm_yyyy = dt.strftime('%d/%m/%Y')
            # Match com "16/03/2026" ou "16/03"
            if dd_mm_yyyy in cell or cell == dd_mm:
                return True
        except ValueError:
            pass
    return False


def escrever_entregas(client, demandas, entregues, semana_str, mes_str, segunda_date_str=None):
    """Atualiza a aba do mês com dados de entregas."""
    ss = client.open_by_key(SHEET_ID)

    abas = ss.worksheets()
    aba = next((a for a in abas if normalizar(a.title) == normalizar(mes_str)), None)
    if not aba:
        print(f"Erro: Aba '{mes_str}' nao encontrada.")
        sys.exit(1)

    print(f"Aba '{aba.title}' acessada.")
    dados = aba.get_all_values()

    updates = []
    for i, row in enumerate(dados):
        # Secao Designers (colunas A-D)
        col_semana, col_nome, col_serem, col_entregues = 0, 1, 2, 3

        semana_linha = str(row[col_semana] if len(row) > col_semana else '').strip()
        nome_linha = str(row[col_nome] if len(row) > col_nome else '').strip()

        if _semana_match(semana_linha, semana_str, segunda_date_str):
            primeiro_nome = match_nome(nome_linha)
            if primeiro_nome and primeiro_nome not in EDITORES:
                nome_team = primeiro_nome
                # Mapear para nome do TEAM
                for uid, tn in TEAM.items():
                    if match_nome(tn) == primeiro_nome:
                        nome_team = tn
                        break
                if demandas.get(nome_team, 0) > 0:
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_serem + 1),
                        'values': [[demandas[nome_team]]]
                    })
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_entregues + 1),
                        'values': [[entregues[nome_team]]]
                    })

        # Secao Editores (colunas G-J)
        col_semana_ed, col_nome_ed, col_serem_ed, col_entregues_ed = 6, 7, 8, 9

        semana_ed = str(row[col_semana_ed] if len(row) > col_semana_ed else '').strip()
        nome_ed = str(row[col_nome_ed] if len(row) > col_nome_ed else '').strip()

        if _semana_match(semana_ed, semana_str, segunda_date_str):
            primeiro_nome_ed = match_nome(nome_ed)
            if primeiro_nome_ed and primeiro_nome_ed in EDITORES:
                nome_team_ed = primeiro_nome_ed
                for uid, tn in TEAM.items():
                    if match_nome(tn) == primeiro_nome_ed:
                        nome_team_ed = tn
                        break
                if demandas.get(nome_team_ed, 0) > 0:
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_serem_ed + 1),
                        'values': [[demandas[nome_team_ed]]]
                    })
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_entregues_ed + 1),
                        'values': [[entregues[nome_team_ed]]]
                    })

    if updates:
        aba.batch_update(updates)
        print(f"Sucesso! {len(updates)//2} colaboradores atualizados (Semana '{semana_str}').")
    else:
        print(f"Nenhuma linha encontrada para Semana '{semana_str}'.")


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='Preencher Entrega de Posts - Stark AV')
    parser.add_argument('--quarta', help='Data da quarta-feira alvo (YYYY-MM-DD)')
    parser.add_argument('--semana', help='Texto da semana (ex: "16/03 a 22/03")')
    parser.add_argument('--mes', help='Nome da aba do mes na planilha')
    parser.add_argument('--dry-run', action='store_true', help='Apenas calcula, sem escrever')
    args = parser.parse_args()

    # Carregar config gerada pela skill
    config_path = '/tmp/entrega_config.json'
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        print(f"Config carregada de {config_path}")
    else:
        print(f"ERRO: {config_path} nao encontrado.")
        print("Execute a skill /preencher-entrega-posts primeiro (ela gera o config).")
        sys.exit(1)

    # Sobrescrever com args CLI se fornecidos
    hoje = datetime.now()

    if not args.quarta:
        args.quarta = config.get('prazo', '')[:10]
        if not args.quarta:
            dias_para_quarta = 2 - hoje.weekday()
            quarta_dt = hoje + timedelta(days=dias_para_quarta)
            args.quarta = quarta_dt.strftime('%Y-%m-%d')

    if not args.semana:
        args.semana = config.get('semana_str', '')
        if not args.semana:
            segunda_dt = hoje - timedelta(days=hoje.weekday())
            domingo_dt = segunda_dt + timedelta(days=6)
            args.semana = f"{segunda_dt.strftime('%d/%m')} a {domingo_dt.strftime('%d/%m')}"

    if not args.mes:
        args.mes = MESES_PT[hoje.month - 1]

    if args.mes == 'Marco':
        args.mes = 'Março'

    prazo_ms = config.get('prazo_ms')
    if not prazo_ms:
        try:
            quarta_date = datetime.strptime(args.quarta, '%Y-%m-%d')
            limite_hora = datetime.combine(quarta_date, time(20, 0, 0))
            prazo_ms = int(limite_hora.timestamp() * 1000)
        except ValueError:
            print("Formato de --quarta invalido. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        prazo_ms = int(prazo_ms)

    print(f"Semana: {args.semana}")
    print(f"Prazo: quarta as 20h (ms: {prazo_ms})")
    print()

    # Carregar tarefas dos JSONs
    tarefas = carregar_tarefas_json(config)

    if not tarefas:
        print("\nNenhuma tarefa encontrada. Possiveis causas:")
        print("  - A skill nao rodou as buscas do ClickUp")
        print("  - Os JSONs em /tmp/clickup_raw_*.json estao vazios")
        sys.exit(1)

    # Calcular entregas
    demandas, entregues = calcular_entregas(tarefas, prazo_ms)

    # Exibir resultados
    print()
    print(f"PRAZO DE ENTREGA DE POSTS - Semana {args.semana}")
    print(f"Meta: {META:.0f}% entregues ate quarta as 20h")
    print()
    print(f"{'Designer/Editor':<20} {'Total':>5} {'Entregues':>10} {'%':>8} {'Meta':>5}")
    print('-' * 52)

    resultados = []
    for nome in TEAM.values():
        total = demandas[nome]
        entreg = entregues[nome]
        if total > 0:
            pct = (entreg / total) * 100
            meta_ok = pct >= META
        else:
            pct = None
            meta_ok = None
        resultados.append((nome, total, entreg, pct, meta_ok))

    com_tarefas = sorted([r for r in resultados if r[3] is not None], key=lambda x: x[3], reverse=True)
    sem_tarefas = [r for r in resultados if r[3] is None]
    resultados = com_tarefas + sem_tarefas

    total_geral = sum(r[1] for r in resultados)
    entregues_geral = sum(r[2] for r in resultados)
    pct_geral = (entregues_geral / total_geral * 100) if total_geral > 0 else 0

    for nome, total, entreg, pct, meta_ok in resultados:
        pct_str = f"{pct:.1f}%" if pct is not None else "N/A"
        meta_str = "SIM" if meta_ok else ("NAO" if meta_ok is not None else "-")
        print(f"{nome:<20} {total:>5} {entreg:>10} {pct_str:>8} {meta_str:>5}")

    print('-' * 52)
    meta_geral_str = "SIM" if pct_geral >= META else "NAO"
    print(f"{'TOTAIS':<20} {total_geral:>5} {entregues_geral:>10} {pct_geral:>7.1f}% {meta_geral_str:>4}")
    print()
    print(f"Media da semana: {pct_geral:.1f}%")

    # Autenticar Google Sheets
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"Erro ao carregar credentials.json: {e}")
        sys.exit(1)

    # Salvar dados brutos
    print(f"\nSalvando dados brutos no Google Sheets...")
    salvar_dados_brutos(client, tarefas, args.semana)

    # Atualizar status
    atualizar_status(client, len(tarefas), 'OK')

    if args.dry_run:
        print("\n(Dry-Run) Nao escrevendo na planilha de Entregas.")
        sys.exit(0)

    # Escrever entregas
    segunda_date_str = config.get('segunda', '')
    print(f"\nEscrevendo na Planilha de Entregas (Mes: {args.mes}, Semana: {args.semana})...")
    escrever_entregas(client, demandas, entregues, args.semana, args.mes, segunda_date_str)
    print(f"\nPlanilha: https://docs.google.com/spreadsheets/d/{SHEET_ID}")


if __name__ == '__main__':
    main()
