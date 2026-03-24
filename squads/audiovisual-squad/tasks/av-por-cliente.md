---
task: AV Por Cliente
agent: av-monitor
version: 1.0.0
elicit: true
mode: interactive
---

# Task: av-por-cliente

Exibe o status completo de produção audiovisual de um cliente específico.

## Inputs

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `cliente` | string | Sim | Nome ou parte do nome do cliente |

## Elicitação

Se `cliente` não for fornecido, perguntar:
```
Qual cliente você quer analisar?

Digite o nome ou parte dele (ex: "Cadu", "Cecília", "Juan"):
```

## Steps

### Step 1: Buscar tarefas com nome do cliente

O nome do cliente aparece no título das tarefas no padrão:
- `Semana DD/MM | [Nome do Cliente]`
- `DD/MM (Dia) - Criativo: Tipo | [Nome do Cliente]`

**Ação:** `clickup_filter_tasks`:
- `list_ids: ["901324888130"]`
- `subtasks: true`
- `order_by: due_date`

Depois, filtrar localmente as tarefas onde o título contém o nome do cliente (case insensitive).

### Step 2: Separar tarefas-mãe de subtarefas

- **Tarefas-mãe** = contêm "Semana" no título → são o contexto da semana (atribuídas ao estrategista)
- **Subtarefas** = contêm data e tipo no título → são os posts individuais (atribuídas ao designer/editor)

### Step 3: Classificar posts por status

Para cada subtarefa (post individual):
- ✅ CONCLUÍDO: edição concluída / concluído
- 🔄 EM ANDAMENTO: edição / revisão
- 🔴 ATRASADO: due_date < hoje E não concluído
- ⏳ PENDENTE: a ser feito, prazo futuro
- ⚠️ SEM DONO: assignees = []

### Step 4: Organizar por semana

Agrupar posts por semana de publicação.

### Step 5: Identificar responsáveis

Para cada post, identificar:
- Quem é o responsável (designer/editor)
- Qual tipo de conteúdo

### Step 6: Calcular progresso do cliente

```
total_posts = count(subtarefas do cliente)
concluidos = count(status concluído)
progresso = (concluidos / total_posts) * 100
posts_atrasados = count(ATRASADO)
```

### Step 7: Exibir status do cliente

## Output Format

```markdown
## 🎯 [Nome do Cliente] — Status de Produção
**Data:** DD/MM/YYYY
**Progresso geral:** N% (N de N posts concluídos)

### Semana Atual

| Data | Dia | Tipo | Responsável | Status |
|------|-----|------|-------------|--------|
| 24/03 | Seg | Carrossel | Eloy Lopes | 🔄 edição |
| 25/03 | Ter | Reels | Ebertty | 🔴 atrasado |
| 26/03 | Qua | Estático | Milena | ⏳ pendente |
| 27/03 | Qui | Carrossel | Eloy | ⏳ pendente |
| 28/03 | Sex | Reels | André | ⏳ pendente |

### Semanas Anteriores

| Semana | Posts | Concluídos | Atrasados |
|--------|-------|------------|-----------|
| 17-21/03 | 5 | 4 | 1 |
| 10-14/03 | 5 | 5 | 0 |

### ⚠️ Atenção
[Listar problemas: sem responsável, atrasados, em risco]

### Responsáveis
- Designer: [Nome]
- Editor: [Nome]
- Estrategista: [Nome]
```

## Veto Conditions

- **VETO** se cliente não encontrado nas tarefas → "Cliente não encontrado. Verifique o nome."
- **VETO** se ClickUp MCP indisponível
- **NUNCA** mostrar posts de outros clientes misturados

## Completion Criteria

- [ ] Identificou todas as tarefas do cliente pelo nome no título
- [ ] Separou tarefas-mãe de subtarefas corretamente
- [ ] Calculou progresso: N de N posts concluídos
- [ ] Organizou por semana
- [ ] Identificou responsáveis por post
- [ ] Destacou atrasados e sem responsável
