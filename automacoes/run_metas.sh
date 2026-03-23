#!/bin/bash
# =====================================================================
# Wrapper para execução agendada da automação de metas AV
# Executado via launchd todo dia 19 às 10:00
# =====================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
LOG_FILE="${LOG_DIR}/metas_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

echo "=== Metas AV — Execução automática ===" >> "$LOG_FILE"
echo "Início: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

/usr/bin/python3 "${SCRIPT_DIR}/metas_av.py" --mes-anterior >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "" >> "$LOG_FILE"
echo "Fim: $(date)" >> "$LOG_FILE"
echo "Exit code: ${EXIT_CODE}" >> "$LOG_FILE"

# Notificação nativa macOS
if [ $EXIT_CODE -eq 0 ]; then
    osascript -e 'display notification "Metas AV do mês anterior foram atualizadas na planilha." with title "Stark — Metas AV" subtitle "Execução automática concluída" sound name "Glass"'
else
    osascript -e 'display notification "Erro ao processar metas. Abrindo log..." with title "Stark — Metas AV" subtitle "Falha na execução" sound name "Basso"'
    # Abre o log automaticamente no editor padrão quando falha
    open "$LOG_FILE"
fi

# Manter apenas os últimos 12 logs
ls -t "${LOG_DIR}"/metas_*.log 2>/dev/null | tail -n +13 | xargs rm -f 2>/dev/null

exit $EXIT_CODE
