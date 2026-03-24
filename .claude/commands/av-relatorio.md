Ative o agente AV Monitor e execute o comando *gerar-relatorio para gerar o relatório completo de performance da equipe audiovisual.

Instruções:
1. Carregue o agente em: squads/audiovisual-squad/agents/av-monitor.md
2. Carregue a task em: squads/audiovisual-squad/tasks/av-gerar-relatorio.md
3. Carregue o template em: squads/audiovisual-squad/templates/relatorio-av-tmpl.md
4. Carregue os dados em: squads/audiovisual-squad/data/av-team-config.yaml
5. Execute as 3 consultas ao ClickUp:
   - clickup_filter_tasks: list_ids ["901324888130"], subtasks: true, order_by: due_date (status geral)
   - Filtrar atrasados: due_date < hoje e status != concluído
   - Filtrar por cada membro da equipe usando assignees
6. Calcule todas as métricas: total, %, por membro, por tipo, por cliente
7. Identifique Top 3 insights (melhor, pior, padrão)
8. Monte o relatório completo usando o template relatorio-av-tmpl.md
9. Exiba o relatório formatado no chat
10. Acione o Gamma MCP (mcp__claude_ai_Gamma__generate) para gerar o documento PDF/apresentação
11. Exiba o link do documento gerado

Período: semana atual (24/03/2026)
Formato: apresentação para liderança
