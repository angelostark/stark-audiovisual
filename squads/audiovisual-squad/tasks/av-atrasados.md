---
task: AV Atrasados
agent: av-monitor
version: 1.0.0
elicit: false
mode: autonomous
---

# Task: av-atrasados

Lista todas as tarefas atrasadas ou em risco na Agenda de Postagem 3.0.

## Definição de Atrasado

| Condição | Classificação |
|----------|---------------|
| due_date < hoje AND status != (concluído, edição concluída) | 🔴 ATRASADO |
| due_date = hoje AND status = "a ser feito" | 🟠 CRÍTICO (risco hoje) |
| due_date <= amanhã AND status = "edição" sem progresso | 🟡 RISCO |
| assignees = [] AND due_date <= amanhã | ⚠️ SEM DONO |

## Steps

### Step 1: Buscar tarefas da lista

**Ação:** `clickup_filter_tasks`:
- `list_ids: ["901324888130"]`
- `subtasks: true`
- `order_by: due_date`
- `include_closed: false`

### Step 2: Filtrar atrasados

Para cada tarefa retornada:
```
hoje = timestamp atual (em ms)
se due_date < hoje E status NOT IN ["edição concluída", "concluído"]:
  → ATRASADO
se due_date == hoje E status == "a ser feito":
  → CRÍTICO
se due_date <= amanhã E status == "edição":
  → RISCO
se assignees == [] E due_date <= amanhã:
  → SEM DONO
```

### Step 3: Agrupar por responsável

Para cada membro em `data/av-team-config.yaml`:
- Listar suas tarefas atrasadas/em risco
- Calcular dias de atraso: `dias = (hoje - due_date) / 86400000`

### Step 4: Listar tarefas sem responsável

Criar seção separada para tarefas com `assignees: []`.

### Step 5: Calcular impacto

Para cada cliente afetado:
- Quantas tarefas atrasadas
- Quais datas vencidas
- Quem deveria estar fazendo

### Step 6: Exibir output

## Output Format

```markdown
## 🔴 Tarefas Atrasadas — DD/MM/YYYY

**Total atrasado:** N tarefas
**Total em risco:** N tarefas
**Clientes afetados:** N

---

### 🔴 Atrasadas (prazo vencido)

#### [Nome do Membro] — N atrasadas
| Tarefa | Cliente | Tipo | Venceu | Dias de atraso | Status atual |
|--------|---------|------|--------|----------------|--------------|
| 22/04 Carrossel | Dra Cecília | Designer | 22/04 | 2 dias | edição |

---

### 🟠 Críticas (vencem hoje)

#### [Nome do Membro]
- DD/MM Tipo | Cliente → status atual

---

### 🟡 Em Risco (vencem amanhã)

#### [Nome do Membro]
- DD/MM Tipo | Cliente → status atual

---

### ⚠️ Sem Responsável (N tarefas)
Tarefas sem ninguém designado:
- DD/MM Tipo | Cliente (vence DD/MM)

---

**Ação recomendada:**
- [X] tarefas precisam de responsável urgente
- [Y] tarefas precisam de aceleração para fechar hoje
```

## Veto Conditions

- **VETO** se ClickUp MCP indisponível
- **VETO** se exibir tarefas concluídas como atrasadas (verificar status corretamente)
- **NUNCA** omitir tarefas sem responsável — são risco real

## Completion Criteria

- [ ] Consultou ClickUp com filtros corretos
- [ ] Calculou dias de atraso corretamente (diferença em ms → dias)
- [ ] Separou: atrasadas / críticas / em risco / sem responsável
- [ ] Agrupou por membro responsável
- [ ] Incluiu seção de "Sem Responsável"
- [ ] Indicou clientes afetados
