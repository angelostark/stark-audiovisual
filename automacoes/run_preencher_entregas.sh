#!/bin/bash
# =====================================================================
# Preencher Entregas — Wrapper para automacao via LaunchAgent
# Executa toda quarta-feira as 20h
#
# Fluxo: Claude CLI (skill MCP) → /tmp/*.json → Python → Sheets
# =====================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${SCRIPT_DIR}/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
LOG_FILE="${LOG_DIR}/preencher_entregas_${TIMESTAMP}.log"

# PATH com locais comuns do Claude CLI e Python
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
# Garantir que Claude CLI nao detecte sessao aninhada
unset CLAUDECODE
cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

echo "=== Preencher Entregas — Execucao automatica ===" >> "$LOG_FILE"
echo "Inicio: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 1. Notificacao de inicio
osascript -e 'display notification "Buscando dados do ClickUp e calculando entregas..." with title "Entregas AV" sound name "Blow"'

# 2. Limpar dados antigos
rm -f /tmp/clickup_filter_week*.json /tmp/clickup_bulk_status_*.json /tmp/entregas_calculadas.json /tmp/entregas_weeks_config.json

# 3. Invocar Claude CLI para buscar dados via MCP e processar
PROMPT="Voce esta rodando em modo automatico (sem interacao humana).

Execute a skill /preencher-entrega-posts seguindo EXATAMENTE as etapas do arquivo .claude/commands/preencher-entrega-posts.md:

1. ETAPA 1: Calcule as semanas do mes atual e salve em /tmp/entregas_weeks_config.json
2. ETAPA 2: Busque tarefas por semana via clickup_filter_tasks (com paginacao). Salve em /tmp/clickup_filter_week*.json
3. ETAPA 3: Busque bulk_time_in_status para tarefas entregues. Salve em /tmp/clickup_bulk_status_*.json
4. ETAPA 4: Execute: python3 automacoes/processar_entregas_raw.py --write

Ao final, imprima exatamente uma linha neste formato:
RESULTADO|total_tarefas|total_membros|total_semanas
Exemplo: RESULTADO|450|9|4"

echo ">>> Invocando Claude CLI..." >> "$LOG_FILE"

/usr/local/bin/claude -p "$PROMPT" --dangerously-skip-permissions >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "Claude CLI exit code: $EXIT_CODE" >> "$LOG_FILE"

# 4. Notificacao de resultado
if [ $EXIT_CODE -eq 0 ]; then
    RESUMO=$(grep "^RESULTADO|" "$LOG_FILE" | tail -1)
    if [ -n "$RESUMO" ]; then
        TAREFAS=$(echo "$RESUMO" | cut -d'|' -f2)
        MEMBROS=$(echo "$RESUMO" | cut -d'|' -f3)
        SEMANAS=$(echo "$RESUMO" | cut -d'|' -f4)
        osascript -e "display notification \"$TAREFAS tarefas, $MEMBROS membros, $SEMANAS semanas\" with title \"Entregas AV\" subtitle \"Planilha atualizada!\" sound name \"Glass\""
    else
        osascript -e "display notification \"Planilha de Entregas atualizada\" with title \"Entregas AV\" sound name \"Glass\""
    fi
else
    osascript -e "display notification \"Erro ao atualizar entregas. Verifique o log.\" with title \"Entregas AV\" subtitle \"Exit: $EXIT_CODE\" sound name \"Basso\""
fi

echo "" >> "$LOG_FILE"
echo "Fim: $(date)" >> "$LOG_FILE"

# 5. Manter apenas os ultimos 12 logs
ls -t "${LOG_DIR}"/preencher_entregas_*.log 2>/dev/null | tail -n +13 | xargs rm -f 2>/dev/null

exit $EXIT_CODE
