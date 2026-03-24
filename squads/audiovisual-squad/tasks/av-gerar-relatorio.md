---
task: AV Gerar Relatório
agent: av-monitor
version: 1.0.0
elicit: true
mode: interactive
---

# Task: av-gerar-relatorio

Gera relatório completo de performance da equipe audiovisual e exporta via Gamma para PDF/apresentação.

## Inputs

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `periodo` | string | Não | Período do relatório. Default: semana atual |
| `formato` | string | Não | "pdf" ou "apresentacao". Default: pdf |

## Elicitação

```
Vou gerar o relatório completo da equipe audiovisual.

Configurações:
1. Período: [semana atual] ou especifique outra (ex: "semana passada", "março")
2. Formato de exportação:
   - PDF (documento para compartilhar)
   - Apresentação (slides para reunião)

Pressione Enter para usar defaults ou responda:
```

## Steps

### Step 1: Coletar dados completos

Executar as 3 consultas ao ClickUp em sequência:

**1.1 — Status geral (todos os posts):**
```
clickup_filter_tasks:
  list_ids: ["901324888130"]
  subtasks: true
  order_by: due_date
```

**1.2 — Tarefas atrasadas:**
Filtrar tarefas onde `due_date < hoje` e status != concluído.

**1.3 — Por membro:**
Para cada membro em `data/av-team-config.yaml`, calcular scorecard individual.

### Step 2: Processar métricas

Calcular:
```
metricas_gerais:
  total_posts: count(all)
  concluidos: count(status in [concluído, edição concluída])
  em_andamento: count(status in [edição, revisão])
  atrasados: count(due_date < hoje AND status not concluído)
  pendentes: count(status = a ser feito AND due_date >= hoje)
  sem_responsavel: count(assignees = [])
  taxa_conclusao: (concluidos / total) * 100

por_membro:
  para_cada_membro:
    - concluidos: N
    - atrasados: N
    - taxa: N%

por_tipo_conteudo:
  carrossel: N
  reels: N
  estatico: N
  reels_3d: N
  capa: N

clientes_com_atraso: [lista]
clientes_ok: [lista]
```

### Step 3: Identificar insights

Analisar e identificar:
- Membro com melhor performance (maior taxa de conclusão)
- Membro com mais atrasos
- Cliente com mais posts atrasados
- Tipo de conteúdo com mais atrasos
- Trend: está melhorando ou piorando vs semana anterior?

### Step 4: Montar relatório com template

Carregar `templates/relatorio-av-tmpl.md` e preencher com os dados coletados.

### Step 5: Exibir relatório no chat

Mostrar o relatório completo formatado em markdown.

### Step 6: Gerar via Gamma

**Ação:** Usar Gamma MCP para gerar documento:
- Montar prompt descritivo com todos os dados
- Chamar `mcp__claude_ai_Gamma__generate` com o conteúdo do relatório
- Aguardar geração
- Exibir link do documento gerado

### Step 7: Confirmar geração

Exibir:
```
✅ Relatório gerado com sucesso!
📄 Link: [URL do Gamma]
📋 Tipo: [PDF / Apresentação]
📅 Período: [período analisado]
```

## Output Format

Ver `templates/relatorio-av-tmpl.md` para estrutura completa.

## Veto Conditions

- **VETO** se ClickUp MCP indisponível → não gerar relatório com dados fictícios
- **VETO** se Gamma MCP indisponível → exibir relatório em markdown e avisar que PDF não foi gerado
- **NUNCA** gerar relatório sem executar as 3 consultas ao ClickUp (status + atrasados + por membro)

## Completion Criteria

- [ ] Executou consulta de status geral ao ClickUp
- [ ] Executou consulta de atrasados
- [ ] Calculou scorecard por membro
- [ ] Calculou todas as métricas: total, %, por tipo, por cliente
- [ ] Identificou pelo menos 3 insights (melhor, pior, padrão)
- [ ] Montou relatório com template
- [ ] Acionou Gamma MCP para geração do documento
- [ ] Exibiu link do documento gerado
