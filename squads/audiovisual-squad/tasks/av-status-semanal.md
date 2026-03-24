---
task: AV Status Semanal
agent: av-monitor
version: 1.0.0
elicit: false
mode: autonomous
---

# Task: av-status-semanal

Busca e exibe o status completo de todas as entregas da semana atual na Agenda de Postagem 3.0.

## Inputs

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `semana` | string | Não | Semana específica (ex: "24/03"). Default: semana atual |

## Preconditions

- [ ] ClickUp MCP disponível
- [ ] Acesso à lista ID: 901324888130

## Steps

### Step 1: Buscar todas as tarefas da lista

**Ação:** Usar `clickup_filter_tasks` com:
- `list_ids: ["901324888130"]`
- `subtasks: true`
- `order_by: due_date`

### Step 2: Classificar por status

Para cada tarefa, classificar em:
- ✅ **CONCLUÍDO**: status = "edição concluída" ou "concluído"
- 🔄 **EM ANDAMENTO**: status = "edição" ou "revisão"
- 🔴 **ATRASADO**: status != concluído E due_date < hoje (timestamp atual)
- ⏳ **PENDENTE**: status = "a ser feito" E due_date >= hoje
- ⚠️ **SEM RESPONSÁVEL**: assignees = [] (qualquer status)

### Step 3: Agrupar por membro responsável

Para cada membro da equipe em `data/av-team-config.yaml`:
- Filtrar tarefas onde `assignees` contém o ID do membro
- Contar por categoria de status

### Step 4: Calcular métricas gerais

```
total = count(all tasks)
concluidas = count(CONCLUÍDO)
em_andamento = count(EM ANDAMENTO)
atrasadas = count(ATRASADO)
pendentes = count(PENDENTE)
sem_responsavel = count(SEM RESPONSÁVEL)
pct_conclusao = (concluidas / total) * 100
```

### Step 5: Identificar Top 3 Riscos

Listar os 3 casos mais críticos:
1. Tarefas ATRASADAS com prazo mais vencido
2. Tarefas SEM RESPONSÁVEL
3. Tarefas em EDIÇÃO com prazo muito próximo (< 1 dia)

### Step 6: Montar e exibir output

Usar template de output abaixo.

## Output Format

```markdown
## 📊 Status Semanal — Agenda de Postagem 3.0
**Data da consulta:** DD/MM/YYYY HH:MM
**Total de tarefas analisadas:** N

### Resumo Geral
| Status | Qtd | % |
|--------|-----|---|
| ✅ Concluído | N | N% |
| 🔄 Em andamento | N | N% |
| 🔴 Atrasado | N | N% |
| ⏳ Pendente | N | N% |
| ⚠️ Sem responsável | N | N% |

### Por Membro da Equipe
#### Designers
| Membro | Concluído | Em andamento | Atrasado | Pendente |
|--------|-----------|--------------|----------|---------|
| Eloy Lopes | N | N | N | N |
| Humberto Sales | N | N | N | N |
| Max Ayalla | N | N | N | N |
| Milena Araújo | N | N | N | N |
| Mateus Deckmann | N | N | N | N |

#### Editores
| Membro | Concluído | Em andamento | Atrasado | Pendente |
|--------|-----------|--------------|----------|---------|
| Ebertty Matnai | N | N | N | N |
| João Andare | N | N | N | N |
| André Araújo | N | N | N | N |

### ⚠️ Top 3 Riscos
1. [Tarefa mais crítica]
2. [Segunda mais crítica]
3. [Terceira mais crítica]

---
*Use `*atrasados` para detalhar os atrasos ou `*gerar-relatorio` para relatório completo.*
```

## Veto Conditions

- **VETO** se ClickUp MCP não responder → "Não foi possível acessar o ClickUp. Verifique a conexão MCP."
- **VETO** se lista retornar 0 tarefas → "Lista vazia ou ID incorreto. Verificar configuração."
- **NUNCA** exibir status sem consultar o ClickUp primeiro

## Completion Criteria

- [ ] Consultou ClickUp com `list_ids: ["901324888130"]` e `subtasks: true`
- [ ] Classificou TODAS as tarefas nas categorias corretas
- [ ] Calculou % de conclusão
- [ ] Identificou e destacou os Top 3 Riscos
- [ ] Exibiu tabela por membro (designers + editores separados)
