# Task: Status do Squad

## Metadata
- **Agent:** orquestrador
- **Command:** `*status`
- **Args:** `[periodo]`

## Descrição
Exibe o status geral do squad: tarefas em andamento, pendentes, atrasadas, e resumo por agente.

## Pré-condições
- [ ] ClickUp acessível via MCP

## Workflow

### STEP 1 — Coletar dados do ClickUp
1. Buscar tarefas ativas do squad de design via ClickUp MCP
2. Filtrar por status: em andamento, pendente, em revisão, atrasado
3. Agrupar por agente/responsável

### STEP 2 — Montar resumo
Para cada categoria:

| Status | Descrição |
|--------|-----------|
| Em andamento | Tarefas sendo executadas agora |
| Pendentes | Aguardando início |
| Em revisão (QA) | Aguardando avaliação do QA |
| Atrasadas | Prazo vencido |
| Concluídas (período) | Finalizadas no período solicitado |

### STEP 3 — Resumo por agente
Mostrar distribuição de carga:

```
## Status do Squad — [data]

### Resumo geral
- Em andamento: [N]
- Pendentes: [N]
- Em revisão: [N]
- Atrasadas: [N]
- Concluídas (semana): [N]

### Por responsável
| Responsável | Andamento | Pendente | QA | Atrasado |
|-------------|-----------|----------|----|----------|
| [nome]      | [N]       | [N]     | [N]| [N]      |
```

### STEP 4 — Alertas
- Listar tarefas atrasadas com nome, cliente e responsável
- Alertar se algum membro está sobrecarregado (>5 tarefas ativas)

## Output esperado
Resumo formatado em tabela com totais e alertas.

## Regras
- Dados SEMPRE do ClickUp — nunca inventar status
- Incluir SEMPRE a data/hora da consulta
- Destacar atrasados em formato de alerta
