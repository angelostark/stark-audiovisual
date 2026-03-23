#!/usr/bin/env python3
"""
Preencher Entrega de Posts — Stark Audiovisual

Lê dados brutos do Google Sheets (alimentado pelo Make.com toda quarta 20h),
calcula % de entrega no prazo por colaborador, e atualiza a planilha de entregas.

Uso:
  python3 preencher_entregas_clickup.py
  python3 preencher_entregas_clickup.py --dry-run
  python3 preencher_entregas_clickup.py --semana "16/03 a 22/03" --quarta 2026-03-18
"""

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

# Planilha alimentada pelo Make.com (dados brutos do ClickUp)
RAW_SHEET_ID = '1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA'

# Planilha de entregas (destino final)
ENTREGAS_SHEET_ID = '1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA'

# =====================================================================
# CONSTANTES DO TIME
# =====================================================================

# UID ClickUp → Primeiro nome
TEAM_UID = {
    82154730:  'Humberto',
    112104835: 'Joao',
    84856123:  'Eloy',
    112104837: 'Max',
    106090854: 'Karyne',
    106172497: 'Milena',
    188585120: 'Ebertty',
    82029622:  'Andre',
    248549658: 'Mateus',
}

# Primeiro nome → Nome completo na planilha de entregas
NOMES = {
    'Eloy':     'Eloy Lopes',
    'Humberto': 'Humberto Salles',
    'Karyne':   'Karyne Torres',
    'Milena':   'Milena Carneiro',
    'Joao':     'João',
    'Max':      'Max',
    'Andre':    'Andre Mello',
    'Ebertty':  'Ebertty Matnai',
    'Mateus':   'Mateus Redmann',
}

# Status que contam como "entregue"
STATUS_ENTREGUE = [
    'done', 'closed', 'edicao concluida', 'aguardando postagem',
    'concluido', 'concluida', 'encerramento da tarefa', 'aprovado',
    'arte aprovada', 'finalizado',
]

META = 97.0

MESES_PT = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

EDITORES = ['Andre', 'Ebertty', 'Mateus']


# =====================================================================
# UTILITARIOS
# =====================================================================

def normalizar(texto):
    """Remove acentos e converte para uppercase."""
    texto = str(texto).strip()
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).upper()


def match_nome(texto):
    """Tenta casar um texto com um dos nomes do time."""
    norm = normalizar(texto)
    for primeiro_nome, completo in NOMES.items():
        if normalizar(primeiro_nome) in norm or normalizar(completo) in norm:
            return primeiro_nome
    return None


def status_entregue(status_str):
    """Verifica se o status (normalizado) indica entrega."""
    norm = normalizar(status_str)
    return any(normalizar(s) in norm for s in STATUS_ENTREGUE)


# =====================================================================
# LEITURA DOS DADOS BRUTOS (GOOGLE SHEETS)
# =====================================================================

def ler_dados_brutos(client, semana_filtro):
    """
    Le a aba 'Dados Brutos' da planilha alimentada pelo Make.com.

    Colunas esperadas:
      A: semana | B: task_id | C: task_name | D: status | E: date_updated
      F: assignee_uid | G: assignee_name | H: parent_name | I: list_id | J: date_created

    Retorna lista de dicts com os dados filtrados pela semana.
    """
    ss = client.open_by_key(RAW_SHEET_ID)

    # Checar aba Status primeiro
    try:
        aba_status = ss.worksheet('Status')
        status_row = aba_status.row_values(2)
        if len(status_row) >= 2:
            ultimo_status = status_row[1].strip().upper()
            ultimo_ts = status_row[0].strip()
            if ultimo_status == 'FALHA':
                print(f"  Make.com reportou FALHA na ultima execucao ({ultimo_ts})")
                print(f"  Erro: {status_row[3] if len(status_row) > 3 else 'sem detalhes'}")
                print(f"  Os dados podem estar incompletos ou desatualizados.\n")
    except Exception:
        pass  # Aba Status pode nao existir ainda

    aba = ss.worksheet('Dados Brutos')
    todos = aba.get_all_values()

    if len(todos) < 2:
        print("Planilha de dados brutos esta vazia. Make.com ainda nao rodou?")
        sys.exit(1)

    headers = [h.strip().lower() for h in todos[0]]
    linhas = todos[1:]

    # Mapear indices das colunas
    col_idx = {}
    for i, h in enumerate(headers):
        col_idx[h] = i

    tarefas = []
    for row in linhas:
        def val(col_name):
            idx = col_idx.get(col_name)
            if idx is not None and idx < len(row):
                return row[idx].strip()
            return ''

        semana = val('semana')

        # Filtrar pela semana solicitada
        if semana_filtro and semana_filtro.lower() not in semana.lower():
            continue

        tarefas.append({
            'task_id': val('task_id'),
            'task_name': val('task_name'),
            'status': val('status'),
            'date_updated': val('date_updated'),
            'assignee_uid': val('assignee_uid'),
            'assignee_name': val('assignee_name'),
            'parent_name': val('parent_name'),
            'list_id': val('list_id'),
        })

    return tarefas


# =====================================================================
# CALCULO DE ENTREGAS
# =====================================================================

def calcular_entregas(tarefas, limite_hora):
    """
    Calcula demandas e entregas no prazo por colaborador.
    Retorna dict {nome: {demandas, entregues_no_prazo}}.
    """
    totais = {nome: {'demandas': 0, 'entregues_no_prazo': 0} for nome in NOMES}

    for t in tarefas:
        # Identificar colaborador pelo UID
        uid_str = t['assignee_uid']
        nome = None
        try:
            uid = int(uid_str)
            nome_key = TEAM_UID.get(uid)
            if nome_key and nome_key in NOMES:
                nome = nome_key
        except (ValueError, TypeError):
            pass

        # Fallback: tentar pelo nome do assignee
        if not nome:
            nome = match_nome(t['assignee_name'])

        if not nome:
            continue

        totais[nome]['demandas'] += 1

        # Checar se entregou no prazo
        if status_entregue(t['status']):
            date_updated_str = t['date_updated']
            try:
                date_updated_ms = int(date_updated_str)
                dt_updated = datetime.fromtimestamp(date_updated_ms / 1000.0)
                if dt_updated <= limite_hora:
                    totais[nome]['entregues_no_prazo'] += 1
            except (ValueError, TypeError):
                # Sem data valida — conta como no prazo se status OK
                totais[nome]['entregues_no_prazo'] += 1

    return totais


# =====================================================================
# ESCRITA NA PLANILHA DE ENTREGAS
# =====================================================================

def escrever_planilha_entregas(client, totais, semana_str, mes_str):
    """Atualiza a planilha de entregas com os dados calculados."""
    ss = client.open_by_key(ENTREGAS_SHEET_ID)

    abas = ss.worksheets()
    aba = next((a for a in abas if normalizar(a.title) == normalizar(mes_str)), None)
    if not aba:
        print(f"Erro: Aba '{mes_str}' nao encontrada na planilha de Entregas.")
        sys.exit(1)

    print(f"Aba '{aba.title}' acessada com sucesso.")
    dados = aba.get_all_values()

    updates = []
    for i, row in enumerate(dados):
        # Secao Designers (colunas A-D)
        col_semana, col_nome, col_serem, col_entregues = 0, 1, 2, 3

        semana_linha = str(row[col_semana] if len(row) > col_semana else '').strip()
        nome_linha = str(row[col_nome] if len(row) > col_nome else '').strip()

        if semana_str.lower() in semana_linha.lower() or semana_linha == '':
            primeiro_nome = match_nome(nome_linha)
            if primeiro_nome and primeiro_nome not in EDITORES:
                if totais[primeiro_nome]['demandas'] > 0:
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_serem + 1),
                        'values': [[totais[primeiro_nome]['demandas']]]
                    })
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_entregues + 1),
                        'values': [[totais[primeiro_nome]['entregues_no_prazo']]]
                    })

        # Secao Editores (colunas G-J)
        col_semana_ed, col_nome_ed, col_serem_ed, col_entregues_ed = 6, 7, 8, 9

        semana_ed = str(row[col_semana_ed] if len(row) > col_semana_ed else '').strip()
        nome_ed = str(row[col_nome_ed] if len(row) > col_nome_ed else '').strip()

        if semana_str.lower() in semana_ed.lower() or semana_ed == '':
            primeiro_nome_ed = match_nome(nome_ed)
            if primeiro_nome_ed and primeiro_nome_ed in EDITORES:
                if totais[primeiro_nome_ed]['demandas'] > 0:
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_serem_ed + 1),
                        'values': [[totais[primeiro_nome_ed]['demandas']]]
                    })
                    updates.append({
                        'range': gspread.utils.rowcol_to_a1(i + 1, col_entregues_ed + 1),
                        'values': [[totais[primeiro_nome_ed]['entregues_no_prazo']]]
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
    parser.add_argument('--mes', help='Nome da aba do mes na planilha de entregas')
    parser.add_argument('--dry-run', action='store_true', help='Apenas calcula, sem escrever')
    args = parser.parse_args()

    if RAW_SHEET_ID == 'PLACEHOLDER_RAW_SHEET_ID':
        print("ERRO: RAW_SHEET_ID nao configurado.")
        print("Edite preencher_entregas_clickup.py e substitua PLACEHOLDER_RAW_SHEET_ID")
        print("pelo ID da planilha 'Dados Entregas AV - Raw' criada no Google Sheets.")
        sys.exit(1)

    # Calcular datas dinamicamente
    hoje = datetime.now()

    if not args.quarta:
        dias_para_quarta = 2 - hoje.weekday()
        quarta_dt = hoje + timedelta(days=dias_para_quarta)
        args.quarta = quarta_dt.strftime('%Y-%m-%d')

    if not args.semana:
        segunda_dt = hoje - timedelta(days=hoje.weekday())
        domingo_dt = segunda_dt + timedelta(days=6)
        args.semana = f"{segunda_dt.strftime('%d/%m')} a {domingo_dt.strftime('%d/%m')}"

    if not args.mes:
        args.mes = MESES_PT[hoje.month - 1]

    if args.mes == 'Marco':
        args.mes = 'Março'

    try:
        quarta_date = datetime.strptime(args.quarta, '%Y-%m-%d')
        limite_hora = datetime.combine(quarta_date, time(20, 0, 0))
    except ValueError:
        print("Formato de --quarta invalido. Use YYYY-MM-DD")
        sys.exit(1)

    print(f"Regra de entrega: Concluido ate {limite_hora.strftime('%d/%m/%Y as %H:%M')}")
    print(f"Semana: {args.semana}")
    print()

    # Autenticar
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"Erro ao carregar credentials.json: {e}")
        sys.exit(1)

    # Ler dados brutos do Google Sheets
    print("Lendo dados brutos do Google Sheets...")
    tarefas = ler_dados_brutos(client, args.semana)
    print(f"Tarefas encontradas para semana '{args.semana}': {len(tarefas)}")

    if not tarefas:
        print("\nNenhuma tarefa encontrada. Possiveis causas:")
        print("  - Make.com ainda nao rodou para essa semana")
        print("  - O formato da semana nao corresponde ao gravado pelo Make.com")
        print(f"  - Tente: --semana \"{args.semana}\"")
        sys.exit(1)

    # Calcular entregas
    totais = calcular_entregas(tarefas, limite_hora)

    # Exibir resultados
    print()
    print(f"PRAZO DE ENTREGA DE POSTS - Semana {args.semana}")
    print(f"Meta: {META:.0f}% entregues ate quarta as 20h")
    print()
    print(f"{'Designer/Editor':<20} {'Total':>5} {'Entregues':>10} {'%':>8} {'Meta':>5}")
    print('-' * 52)

    resultados = []
    for nome in NOMES:
        d = totais[nome]
        total = d['demandas']
        entreg = d['entregues_no_prazo']
        if total > 0:
            pct = (entreg / total) * 100
            meta_ok = pct >= META
        else:
            pct = None
            meta_ok = None
        resultados.append((nome, total, entreg, pct, meta_ok))

    # Ordenar: maior % primeiro
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
    print(f"Planilha: https://docs.google.com/spreadsheets/d/{ENTREGAS_SHEET_ID}")

    # Escrever na planilha de entregas
    if args.dry_run:
        print("\n(Dry-Run) Nao escrevendo na planilha de Entregas.")
        sys.exit(0)

    print(f"\nEscrevendo na Planilha de Entregas (Mes: {args.mes}, Semana: {args.semana})...")
    escrever_planilha_entregas(client, totais, args.semana, args.mes)


if __name__ == '__main__':
    main()
