Ative o agente AV Monitor e execute o comando *por-membro com o argumento fornecido pelo usuário.

Se o usuário digitou `/av-membro Eloy`, o argumento é "Eloy".
Se nenhum argumento foi fornecido, pergunte: "Qual membro da equipe você quer analisar?"

Instruções:
1. Carregue o agente em: squads/audiovisual-squad/agents/av-monitor.md
2. Carregue a task em: squads/audiovisual-squad/tasks/av-por-membro.md
3. Carregue os dados em: squads/audiovisual-squad/data/av-team-config.yaml
4. Resolva o ID do membro com base no nome informado
5. Use o ClickUp MCP com filtro por assignee: clickup_filter_tasks com list_ids: ["901324888130"] e assignees: ["{user_id}"]
6. Execute a task av-por-membro seguindo exatamente as instruções do arquivo
7. Exiba o scorecard completo do membro

Argumento do usuário: $ARGUMENTS
