#!/bin/bash
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH

cd /Users/angelogabriel/Documents/AIOS-CRIADOR

# Notificacao de inicio
osascript -e 'display notification "Lendo dados do Google Sheets e calculando entregas..." with title "Entregas AV"'

# Executa o Python script
python3 automacoes/preencher_entregas_clickup.py > /tmp/entregas_cron.log 2>&1
STATUS=$?

if [ $STATUS -eq 0 ]; then
    osascript -e 'display notification "Planilha de Entregas atualizada com sucesso!" with title "Entregas AV"'
else
    osascript -e 'display notification "Erro ao atualizar Planilha. Verifique /tmp/entregas_cron.log" with title "Entregas AV"'
fi
