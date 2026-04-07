# Automacao de Metas Audiovisual

Voce e o **agente av-monitor** executando a task `*metas` da squad audiovisual.

**OBRIGATORIO:** Carregue e siga EXATAMENTE o workflow da task:
`squads/audiovisual-squad/tasks/av-metas.md`

## Resumo do fluxo

1. Determinar mes/ano alvo
2. **Prazo de Entrega**: calcular via ClickUp MCP (todas as semanas do mes)
3. **Layouts/Videos/Alteracoes**: ler das planilhas Google (via gspread)
4. Apresentar resultados e pedir confirmacao
5. Gravar na planilha de Metas AV
6. Enviar DMs via ClickUp Chat
7. Reportar resultado final

## Argumentos do usuario

- Sem argumentos → perguntar o periodo
- `$ARGUMENTS` → pode conter: mes especifico, "mes anterior", "--skip-chat"

## Referencia rapida

- Task completa: `squads/audiovisual-squad/tasks/av-metas.md`
- Config do time: `squads/audiovisual-squad/data/av-team-config.yaml`
- Planilha destino: `1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc`
- ClickUp List: `901324888130` (Agenda de Postagem 3.0)

## IMPORTANTE

- SEMPRE rodar dry-run / simulacao antes de gravar
- NUNCA gravar sem confirmacao explicita
- Prazo de Entrega vem do ClickUp MCP, NAO da planilha de entregas
- Demais KPIs vem das planilhas Google (leitura via Python/gspread)
