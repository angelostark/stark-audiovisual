---
task: AV Por Membro
agent: av-monitor
version: 1.0.0
elicit: true
mode: interactive
---

# Task: av-por-membro

Gera scorecard detalhado de entregas de um membro específico da equipe audiovisual.

## Inputs

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `membro` | string | Sim | Nome ou parte do nome do membro |

## Elicitação

Se `membro` não for fornecido, perguntar:
```
Qual membro da equipe você quer analisar?

Designers: Eloy Lopes, Humberto Sales, Max Ayalla, Milena Araújo, João Andare, Karyne Torres
Editores: Ebertty Matnai, Mateus Deckmann Redmann, André Araújo
Estrategistas: Matheus Peleteiro, Bruna Santana, Thaynara Castro, Evany Bandeira, Daniela Cabral, Germana Souza

Digite o nome (ou parte dele):
```

## Steps

### Step 1: Resolver membro

Buscar em `data/av-team-config.yaml` o membro que corresponde ao nome informado.
Usar busca parcial (case insensitive): "eloy" → "Eloy Lopes" (ID: 84856123).

Se ambíguo (ex: "max" encontra mais de um), listar opções e pedir confirmação.

### Step 2: Buscar tarefas do membro

**Ação:** `clickup_filter_tasks`:
- `list_ids: ["901324888130"]`
- `assignees: ["{user_id}"]`
- `subtasks: true`
- `order_by: due_date`

### Step 3: Classificar tarefas

Para cada tarefa do membro:
- ✅ CONCLUÍDO: status = "edição concluída" ou "concluído"
- 🔄 EM ANDAMENTO: status = "edição" ou "revisão"
- 🔴 ATRASADO: due_date < hoje E status != concluído
- ⏳ PENDENTE: status = "a ser feito" E due_date >= hoje

### Step 4: Calcular métricas individuais

```
total = count(all)
taxa_conclusao = (concluidas / total) * 100
dias_medio_atraso = média de (hoje - due_date) para atrasadas
clientes_atendidos = unique(clientes nas tarefas)
tipos_conteudo = unique(tipos extraídos do nome da tarefa)
```

### Step 5: Identificar padrão

Verificar:
- Qual tipo de conteúdo tem mais atraso?
- Quais clientes estão mais atrasados?
- Há tarefas em "edição" há muito tempo?

### Step 6: Exibir scorecard

## Output Format

```markdown
## 👤 [Nome do Membro] — Scorecard Audiovisual
**Função:** [Designer / Editor / Estrategista]
**Data:** DD/MM/YYYY

### Resumo
| Métrica | Valor |
|---------|-------|
| Total de tarefas | N |
| ✅ Concluídas | N (N%) |
| 🔄 Em andamento | N |
| 🔴 Atrasadas | N |
| ⏳ Pendentes | N |
| **Taxa de conclusão** | **N%** |

### Clientes Atendidos
[Lista de clientes com qtd de posts cada]

### Tipos de Conteúdo
[Carrossel: N | Reels: N | Estático: N | ...]

### Detalhe das Tarefas

#### 🔴 Atrasadas
| Tarefa | Cliente | Venceu | Dias de atraso |
|--------|---------|--------|----------------|

#### 🔄 Em Andamento
| Tarefa | Cliente | Prazo | Status |
|--------|---------|-------|--------|

#### ✅ Concluídas
[Lista resumida]

#### ⏳ Pendentes
[Lista com prazo]

### ⚠️ Pontos de Atenção
[Padrão identificado: ex. "3 de 5 atrasos são Reels do Dr. Cadu"]
```

## Veto Conditions

- **VETO** se membro não encontrado em `av-team-config.yaml` → listar membros disponíveis
- **VETO** se ClickUp MCP indisponível
- **NUNCA** mostrar tarefas de outros membros no scorecard individual

## Completion Criteria

- [ ] Resolveu o ID do membro corretamente
- [ ] Filtrou tarefas pelo assignee correto via ClickUp MCP
- [ ] Calculou taxa de conclusão
- [ ] Identificou padrão de atraso (tipo ou cliente recorrente)
- [ ] Exibiu scorecard completo com todas as seções
