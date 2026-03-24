---
checklist: AV Monitor Quality Gate
agent: av-monitor
version: 1.0.0
applies_to: [status-semanal, atrasados, por-membro, por-cliente, gerar-relatorio]
---

# Checklist: AV Monitor Quality Gate

Validação de qualidade para todos os outputs do agente AV Monitor.

---

## 🔴 BLOQUEANTES — VETO se qualquer um falhar

### Dados
- [ ] **Fonte real:** Dados foram buscados do ClickUp via MCP (não inventados)
- [ ] **Lista correta:** Consulta usou `list_ids: ["901324888130"]` (Agenda de Postagem 3.0)
- [ ] **Subtarefas incluídas:** `subtasks: true` na consulta
- [ ] **Total declarado:** Output mostra total de tarefas analisadas
- [ ] **Data da consulta:** Output inclui data/hora da busca

### Classificação
- [ ] **Atrasados corretos:** Tarefa é atrasada somente se `due_date < hoje` E status não concluído
- [ ] **Concluídos corretos:** Somente status "edição concluída" ou "concluído" = concluído
- [ ] **Sem responsável:** Tarefas com `assignees: []` estão identificadas separadamente
- [ ] **% calculada:** Taxa de conclusão está presente no output

### Integridade
- [ ] **Sem dados inventados:** Nenhum número ou status foi estimado sem consulta real
- [ ] **Sem omissões:** Atrasados NÃO foram ocultados para evitar má notícia
- [ ] **Membro correto:** Se filtrou por membro, usou o ID correto do ClickUp

---

## 🟡 RECOMENDADOS — WARNING se ausente

### Completude
- [ ] Top 3 riscos identificados no status geral
- [ ] Tarefas sem responsável têm seção própria
- [ ] Clientes afetados estão listados nos atrasados
- [ ] Tipo de conteúdo identificado em cada tarefa

### Análise
- [ ] Padrão de atraso identificado (membro recorrente ou cliente recorrente)
- [ ] Recomendação de ação presente nos relatórios
- [ ] Comparação com semana anterior quando possível

### Relatório PDF
- [ ] Gamma MCP foi acionado para geração
- [ ] Link do documento está no output
- [ ] Período do relatório está claro no documento

---

## Aprovação

| Critério | Resultado |
|----------|-----------|
| 100% bloqueantes passando | APROVADO ✅ |
| Qualquer bloqueante falhando | VETADO 🔴 |
| < 80% recomendados | WARNING 🟡 |

---

## Veto Conditions Automáticas

```yaml
veto_if:
  - condition: "ClickUp MCP não respondeu"
    action: "VETO — não exibir dados. Informar falha de conexão."
  - condition: "Lista retornou 0 tarefas"
    action: "VETO — verificar se list_id está correto"
  - condition: "Status exibido sem consulta ao ClickUp"
    action: "VETO — dados fabricados são inaceitáveis"
  - condition: "Atrasados omitidos intencionalmente"
    action: "VETO — o líder precisa da verdade completa"
```
