#!/usr/bin/env python3
"""
Processar Entregas Raw — Stark Audiovisual

Lê resultados brutos de clickup_filter_tasks e clickup_get_bulk_tasks_time_in_status
salvos em /tmp/ pela skill, calcula entregas no prazo por membro/semana,
e gera /tmp/entregas_calculadas.json para uso pelo preencher_entregas_clickup.py.

Uso:
  python3 processar_entregas_raw.py
  python3 processar_entregas_raw.py --write   # processa E escreve na planilha
"""

import json
import glob
import os
import sys
import argparse
import subprocess

# =====================================================================
# CONSTANTES
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

STATUS_ENTREGUE = [
    'done', 'closed', 'edição concluída', 'aguardando postagem',
    'concluído', 'concluída', 'encerramento da tarefa', 'aprovado',
    'arte aprovada', 'finalizado',
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREENCHER_SCRIPT = os.path.join(SCRIPT_DIR, 'preencher_entregas_clickup.py')
OUTPUT_PATH = '/tmp/entregas_calculadas.json'


# =====================================================================
# CARREGAR DADOS
# =====================================================================

def carregar_config_semanas():
    """Lê /tmp/entregas_weeks_config.json com definições das semanas."""
    path = '/tmp/entregas_weeks_config.json'
    if not os.path.exists(path):
        print(f"ERRO: {path} nao encontrado.")
        print("A skill deve gerar esse arquivo antes de rodar este script.")
        sys.exit(1)

    with open(path) as f:
        config = json.load(f)

    print(f"Config carregada: {config['mes']}, {len(config['semanas'])} semanas")
    return config


def carregar_filter_tasks():
    """Lê todos os /tmp/clickup_filter_week*.json."""
    tarefas_por_semana = {}
    files = sorted(glob.glob('/tmp/clickup_filter_week*.json'))

    if not files:
        print("ERRO: Nenhum arquivo /tmp/clickup_filter_week*.json encontrado.")
        sys.exit(1)

    for filepath in files:
        # Extrair número da semana do nome: clickup_filter_week1_p0.json
        basename = os.path.basename(filepath)
        # Parse week number
        parts = basename.replace('clickup_filter_week', '').replace('.json', '')
        week_num = parts.split('_')[0]

        with open(filepath) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"  Arquivo corrompido: {filepath}")
                continue

        # Extrair tarefas
        tasks = []
        if isinstance(data, dict):
            tasks = data.get('tasks', data.get('results', data.get('items', [])))
        elif isinstance(data, list):
            tasks = data

        if week_num not in tarefas_por_semana:
            tarefas_por_semana[week_num] = {}

        for task in tasks:
            tid = task.get('id')
            if tid:
                tarefas_por_semana[week_num][tid] = task

    total = sum(len(t) for t in tarefas_por_semana.values())
    print(f"Filter tasks carregados: {total} tarefas em {len(tarefas_por_semana)} semanas")
    return tarefas_por_semana


def carregar_bulk_status():
    """Lê todos os /tmp/clickup_bulk_status_*.json."""
    timestamps = {}  # task_id -> timestamp_ms de entrega
    files = sorted(glob.glob('/tmp/clickup_bulk_status_*.json'))

    if not files:
        print("AVISO: Nenhum arquivo de bulk status encontrado. Usando fallback date_updated.")
        return timestamps

    for filepath in files:
        with open(filepath) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"  Arquivo corrompido: {filepath}")
                continue

        # O formato pode variar - tratar ambos os formatos
        if isinstance(data, dict):
            for task_id, info in data.items():
                if task_id in ('status', 'error', 'message'):
                    continue

                status_history = None
                if isinstance(info, dict):
                    status_history = info.get('status_history', info.get('statusHistory', []))
                elif isinstance(info, list):
                    status_history = info

                if not status_history:
                    continue

                # Encontrar o timestamp mais recente de um status de entrega
                for entry in status_history:
                    status_name = str(entry.get('status', '')).lower().strip()
                    if status_name in STATUS_ENTREGUE:
                        since = entry.get('since')
                        if since:
                            try:
                                ts = int(since)
                                # Manter o timestamp mais recente de entrega
                                if task_id not in timestamps or ts > timestamps[task_id]:
                                    timestamps[task_id] = ts
                            except (ValueError, TypeError):
                                pass

    print(f"Bulk status carregados: {len(timestamps)} tarefas com timestamp de entrega")
    return timestamps


# =====================================================================
# PROCESSAR
# =====================================================================

def processar(config, tarefas_por_semana, timestamps):
    """Calcula entregas por membro por semana."""
    resultado = {
        'mes': config['mes'],
        'semanas': []
    }

    for semana_def in config['semanas']:
        week_num = str(semana_def['week_num'])
        segunda = semana_def['segunda']
        deadline_ms = int(semana_def['deadline_ms'])
        semana_str = semana_def.get('semana_str', '')

        tarefas = tarefas_por_semana.get(week_num, {})

        # Contar por membro
        membros = {}
        for nome in TEAM.values():
            membros[nome] = {'total': 0, 'entregues': 0}

        for tid, task in tarefas.items():
            # Extrair status
            status_raw = task.get('status', '')
            if isinstance(status_raw, dict):
                status_str = status_raw.get('status', '').lower().strip()
            else:
                status_str = str(status_raw).lower().strip()

            is_entregue = status_str in STATUS_ENTREGUE

            # Verificar entrega no prazo
            entregue_no_prazo = False
            if is_entregue:
                # Prioridade: bulk status timestamp > date_done > date_updated
                ts = timestamps.get(tid)
                if ts is None:
                    # Fallback: date_done ou date_updated da tarefa
                    dd = task.get('date_done') or task.get('dateDone')
                    if dd:
                        try:
                            ts = int(dd)
                        except (ValueError, TypeError):
                            pass
                if ts is None:
                    du = task.get('date_updated') or task.get('dateUpdated')
                    if du:
                        try:
                            ts = int(du)
                        except (ValueError, TypeError):
                            pass

                if ts is not None:
                    entregue_no_prazo = ts <= deadline_ms
                else:
                    # Sem timestamp nenhum - contar como entregue (melhor que perder)
                    entregue_no_prazo = True

            # Atribuir a cada membro assignee
            assignees = task.get('assignees', [])
            for a in assignees:
                uid = a.get('id') or a.get('uid')
                try:
                    uid = int(uid)
                except (ValueError, TypeError):
                    continue
                nome = TEAM.get(uid)
                if not nome:
                    continue

                membros[nome]['total'] += 1
                if entregue_no_prazo:
                    membros[nome]['entregues'] += 1

        # Remover membros sem tarefas
        membros_com_tarefas = {n: v for n, v in membros.items() if v['total'] > 0}

        resultado['semanas'].append({
            'semana_str': semana_str,
            'segunda': segunda,
            'deadline_ms': deadline_ms,
            'membros': membros_com_tarefas,
        })

        # Log
        total_sem = sum(v['total'] for v in membros_com_tarefas.values())
        entreg_sem = sum(v['entregues'] for v in membros_com_tarefas.values())
        pct = (entreg_sem / total_sem * 100) if total_sem > 0 else 0
        print(f"  Semana {semana_str}: {entreg_sem}/{total_sem} = {pct:.1f}% ({len(membros_com_tarefas)} membros)")

    return resultado


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='Processar entregas raw do ClickUp')
    parser.add_argument('--write', action='store_true', help='Alem de processar, escrever na planilha')
    parser.add_argument('--dry-run', action='store_true', help='Nao escrever na planilha')
    args = parser.parse_args()

    print("=== Processar Entregas Raw ===\n")

    # Carregar dados
    config = carregar_config_semanas()
    tarefas_por_semana = carregar_filter_tasks()
    timestamps = carregar_bulk_status()

    print()

    # Processar
    resultado = processar(config, tarefas_por_semana, timestamps)

    # Salvar resultado
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print(f"\nResultado salvo em {OUTPUT_PATH}")

    # Resumo
    total_geral = sum(
        sum(m['total'] for m in s['membros'].values())
        for s in resultado['semanas']
    )
    entreg_geral = sum(
        sum(m['entregues'] for m in s['membros'].values())
        for s in resultado['semanas']
    )
    pct = (entreg_geral / total_geral * 100) if total_geral > 0 else 0
    print(f"TOTAL GERAL: {entreg_geral}/{total_geral} = {pct:.1f}%")

    # Escrever na planilha
    if args.write and not args.dry_run:
        print(f"\nEscrevendo na planilha...")
        cmd = [sys.executable, PREENCHER_SCRIPT, '--input', OUTPUT_PATH]
        result = subprocess.run(cmd, capture_output=False)
        sys.exit(result.returncode)
    elif args.write and args.dry_run:
        print(f"\n(Dry-Run) Executando sem escrever...")
        cmd = [sys.executable, PREENCHER_SCRIPT, '--input', OUTPUT_PATH, '--dry-run']
        subprocess.run(cmd, capture_output=False)


if __name__ == '__main__':
    main()
