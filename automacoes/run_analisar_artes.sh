#!/bin/bash
# =====================================================================
# Analisar Artes — Wrapper para automacao via LaunchAgent
# Uso: run_analisar_artes.sh [daily|weekly]
#
# daily  -> analisa artes do dia (seg-sex 10h)
# weekly -> analisa artes da semana + resumo semanal (sex 18h)
# =====================================================================

MODE="${1:-daily}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${SCRIPT_DIR}/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
LOG_FILE="${LOG_DIR}/analisar_artes_${TIMESTAMP}.log"
JSON_FILE="/tmp/analise_artes_result_${TIMESTAMP}.json"

# PATH com locais comuns do Claude CLI e Python
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
# Garantir que Claude CLI nao detecte sessao aninhada (necessario se rodando de dentro do Claude Code)
unset CLAUDECODE
cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

echo "=== Analisar Artes — Execucao automatica ($MODE) ===" >> "$LOG_FILE"
echo "Inicio: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Determinar periodo
if [ "$MODE" = "weekly" ]; then
    PERIOD="week"
    TITLE="Analise Semanal de Artes"
    MAX_FILES=50
else
    PERIOD="today"
    TITLE="Analise Diaria de Artes"
    MAX_FILES=30
fi

# 1. Notificacao de inicio
osascript -e "display notification \"Baixando artes do Drive ($PERIOD)...\" with title \"$TITLE\" sound name \"Blow\""

# 2. Baixar imagens do Drive
echo ">>> Baixando imagens (--client all --period $PERIOD --max-files $MAX_FILES)" >> "$LOG_FILE"

python3 automacoes/analisar_artes.py \
    --client all \
    --period "$PERIOD" \
    --max-files "$MAX_FILES" \
    --json-output "$JSON_FILE" \
    >> "$LOG_FILE" 2>&1

DOWNLOAD_EXIT=$?
echo "Download exit code: $DOWNLOAD_EXIT" >> "$LOG_FILE"

if [ $DOWNLOAD_EXIT -ne 0 ]; then
    osascript -e "display notification \"Erro ao baixar artes do Drive. Verifique o log.\" with title \"$TITLE\" sound name \"Basso\""
    echo "ERRO: Falha no download de artes" >> "$LOG_FILE"
    open "$LOG_FILE"
    exit 1
fi

# 3. Verificar se encontrou imagens
TOTAL=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d.get('total_images',0))" 2>/dev/null)

if [ "$TOTAL" = "0" ] || [ -z "$TOTAL" ]; then
    osascript -e "display notification \"Nenhuma arte encontrada para $PERIOD\" with title \"$TITLE\" sound name \"Purr\""
    echo "Nenhuma arte encontrada para o periodo" >> "$LOG_FILE"
    echo "Fim: $(date)" >> "$LOG_FILE"
    rm -f "$JSON_FILE"
    exit 0
fi

echo ">>> $TOTAL imagens encontradas. Iniciando analise com Claude CLI..." >> "$LOG_FILE"

# 4. Invocar Claude Code CLI para analise visual
# Heredoc SEM aspas para permitir expansao de $JSON_FILE e $MODE
osascript -e "display notification \"Analisando $TOTAL artes contra Design System...\" with title \"$TITLE\" sound name \"Blow\""

PROMPT="Voce esta rodando em modo automatico (sem interacao humana).

1. Leia o arquivo JSON em ${JSON_FILE} para obter a lista de imagens baixadas.

2. Para cada imagem listada no campo images:
   - Use a tool Read no campo local_path para visualizar a imagem
   - Avalie contra as 16 regras do Design System Stark (confira .claude/commands/analisar-artes.md)
   - Atribua para cada regra: OK, ALERTA ou FALHA
   - Calcule score: OK=100, ALERTA=50, FALHA=0, media das 16 regras

3. Grave resultados no Google Sheets (ID: 1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I):
   - Aba Avaliacoes: uma linha por arte (data, cliente, designer, nome_arquivo, score, classificacao, veredicto_por_regra)
   - Se mode = ${MODE}: e mode for weekly, preencha tambem a aba Resumo Semanal com agregado por designer (media scores, total artes, alertas frequentes)

4. Ao final, imprima exatamente uma linha neste formato (sem espacos extras):
   RESULTADO|total_artes|score_medio_percentual|classificacao
   Exemplo: RESULTADO|12|78|BOM
   Classificacao: EXCELENTE (>=90), BOM (>=70), ATENCAO (>=50), CRITICO (<50)"

/usr/local/bin/claude -p "$PROMPT" --dangerously-skip-permissions >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# 5. Notificacao de resultado
if [ $EXIT_CODE -eq 0 ]; then
    RESUMO=$(grep "^RESULTADO|" "$LOG_FILE" | tail -1)
    if [ -n "$RESUMO" ]; then
        ARTES=$(echo "$RESUMO" | cut -d'|' -f2)
        SCORE=$(echo "$RESUMO" | cut -d'|' -f3)
        CLASS=$(echo "$RESUMO" | cut -d'|' -f4)
        osascript -e "display notification \"$ARTES artes — Score $SCORE% ($CLASS)\" with title \"$TITLE\" subtitle \"Resultados gravados no Sheets\" sound name \"Glass\""
    else
        osascript -e "display notification \"$TOTAL artes analisadas\" with title \"$TITLE\" subtitle \"Verifique o Sheets\" sound name \"Glass\""
    fi
else
    osascript -e "display notification \"Erro na analise. Verifique o log.\" with title \"$TITLE\" subtitle \"Exit code: $EXIT_CODE\" sound name \"Basso\""
    open "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "Fim: $(date)" >> "$LOG_FILE"
echo "Exit code: $EXIT_CODE" >> "$LOG_FILE"

# 6. Limpeza
rm -f "$JSON_FILE"
# Manter apenas os ultimos 12 logs
ls -t "${LOG_DIR}"/analisar_artes_*.log 2>/dev/null | tail -n +13 | xargs rm -f 2>/dev/null

exit $EXIT_CODE
