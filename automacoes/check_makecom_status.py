#!/usr/bin/env python3
"""
Checa o status da última execução do cenário Make.com
lendo a aba "Status" da planilha "Dados Entregas AV - Raw".

Dispara notificação macOS se:
- Última execução falhou
- Dados estão desatualizados (Make.com não rodou)

Uso:
  python3 check_makecom_status.py
  python3 check_makecom_status.py --sheet-id XXXXX  # override do sheet ID
"""

import json
import os
import subprocess
import sys
import argparse
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# ID da planilha "Dados Entregas AV - Raw" — SUBSTITUIR PELO ID REAL
DEFAULT_SHEET_ID = '1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA'


def notificar(titulo, mensagem, som=True):
    """Envia notificação macOS via osascript."""
    som_str = ' sound name "Blow"' if som else ''
    script = f'display notification "{mensagem}" with title "{titulo}"{som_str}'
    subprocess.run(['osascript', '-e', script], check=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sheet-id', default=DEFAULT_SHEET_ID,
                        help='ID da planilha Google Sheets')
    args = parser.parse_args()

    try:
        import gspread
    except ImportError:
        print("gspread não instalado. Rode: pip3 install gspread")
        notificar("Entregas AV", "Erro: gspread não instalado. Rode pip3 install gspread")
        sys.exit(1)

    if args.sheet_id == 'PLACEHOLDER_SHEET_ID':
        print("Sheet ID não configurado. Edite DEFAULT_SHEET_ID no script.")
        notificar("Entregas AV", "Sheet ID não configurado no check_makecom_status.py")
        sys.exit(1)

    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        client = gspread.authorize(creds)
        ss = client.open_by_key(args.sheet_id)
    except Exception as e:
        print(f"Erro ao conectar ao Google Sheets: {e}")
        notificar("Entregas AV - ERRO", f"Não consegui acessar a planilha: {e}")
        sys.exit(1)

    # Ler aba "Status"
    try:
        aba_status = ss.worksheet("Status")
        dados = aba_status.get_all_values()
    except Exception:
        print("Aba 'Status' não encontrada na planilha.")
        notificar("Entregas AV - ERRO", "Aba 'Status' não existe na planilha de dados brutos.")
        sys.exit(1)

    # Esperado: linha 1 = header, linha 2 = última execução
    # Colunas: A=timestamp, B=status, C=tasks_count, D=error_message
    if len(dados) < 2:
        notificar("Entregas AV - ALERTA",
                  "Make.com nunca rodou. Planilha de status está vazia.")
        sys.exit(1)

    row = dados[1]  # linha 2 (última execução)
    timestamp_str = row[0] if len(row) > 0 else ''
    status = row[1].strip().upper() if len(row) > 1 else ''
    tasks_count = row[2] if len(row) > 2 else '0'
    error_msg = row[3] if len(row) > 3 else ''

    # Checar se o timestamp é recente (últimas 48h)
    agora = datetime.now()
    try:
        ultima_exec = datetime.fromisoformat(timestamp_str)
        horas_atras = (agora - ultima_exec).total_seconds() / 3600
    except (ValueError, TypeError):
        horas_atras = 999

    if status == 'FALHA' or status == 'ERRO':
        notificar(
            "Entregas AV - FALHA",
            f"Make.com falhou na quarta! Erro: {error_msg[:80]}",
            som=True
        )
        print(f"FALHA detectada: {error_msg}")
        sys.exit(2)

    if horas_atras > 48:
        notificar(
            "Entregas AV - ALERTA",
            f"Make.com não rodou há {int(horas_atras)}h. Última exec: {timestamp_str}",
            som=True
        )
        print(f"Dados desatualizados: última execução há {int(horas_atras)}h")
        sys.exit(3)

    if status == 'OK':
        print(f"Tudo certo. Última exec: {timestamp_str}, {tasks_count} tarefas coletadas.")
        # Notificação silenciosa de sucesso (sem som)
        notificar("Entregas AV", f"Make.com OK — {tasks_count} tarefas coletadas.", som=False)
        sys.exit(0)

    # Status desconhecido
    notificar("Entregas AV - ALERTA", f"Status desconhecido: '{status}'")
    sys.exit(4)


if __name__ == '__main__':
    main()
