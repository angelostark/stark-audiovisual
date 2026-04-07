---
task: Refacoes por Cliente
responsavel: "@monitor-refacoes"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Nome do cliente (ou 'todos')
  - Periodo (padrao: ultimos 30 dias)
Saida: |
  - Ranking de clientes por volume de refacao
  - Causas recorrentes por cliente
  - Sugestao de acao (briefing, identidade, etc.)
Checklist:
  - "[ ] Filtrar refacoes por cliente"
  - "[ ] Identificar causas recorrentes"
  - "[ ] Classificar: briefing vago, identidade nao seguida, regra Stark violada"
  - "[ ] Gerar ranking ordenado por volume"
  - "[ ] Sugerir acoes por cliente"
---

# *refacoes-por-cliente

Analisa refacoes agrupadas por cliente, identifica causas recorrentes e sugere acoes corretivas.

## Uso

```
*refacoes-por-cliente "todos"
*refacoes-por-cliente --cliente "Dra. Camila" --periodo "60 dias"
*refacoes-por-cliente "Dr. Cadu"
```

## Fluxo

1. Filtrar refacoes por cliente (ou todos)
2. Identificar causas recorrentes por cliente:
   - Briefing vago (informacoes insuficientes)
   - Identidade nao seguida (paleta/fontes erradas)
   - Regra Stark violada (itens proibidos)
3. Gerar ranking ordenado por volume de refacoes
4. Sugerir acoes especificas por cliente:
   - Briefing vago → melhorar template de briefing
   - Identidade nao seguida → atualizar Brand Guardian
   - Regras Stark → reforcar treinamento

## Regras

- Alertar gestor quando cliente atinge 3+ refacoes no mes
- Classificar causas: briefing, identidade, regra Stark, acabamento
- Sugestoes devem ser acionaveis e especificas
- Periodo padrao: ultimos 30 dias
