---
task: Refacoes por Designer
responsavel: "@monitor-refacoes"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Nome do designer (ou 'todos')
  - Periodo (padrao: ultimos 30 dias)
Saida: |
  - Criterios mais falhados por designer
  - Evolucao comparada com periodo anterior
  - Pontos fortes identificados
Checklist:
  - "[ ] Filtrar refacoes por designer"
  - "[ ] Agrupar por criterio QA mais falhado"
  - "[ ] Calcular evolucao (melhorou/piorou)"
  - "[ ] Identificar pontos fortes do designer"
  - "[ ] Formatar relatorio individual"
---

# *refacoes-por-designer

Analisa refacoes por designer, identifica criterios mais falhados e acompanha evolucao.

## Uso

```
*refacoes-por-designer "todos"
*refacoes-por-designer --designer "Humberto" --periodo "60 dias"
*refacoes-por-designer "Eloy"
```

## Fluxo

1. Filtrar refacoes por designer (ou todos)
2. Agrupar por criterio QA mais falhado:
   - Criatividade e inovacao
   - Elementos obrigatorios
   - Regras Stark
   - Hierarquia e legibilidade
   - Acabamento tecnico
3. Calcular evolucao comparando com periodo anterior:
   - Melhorou: menos refacoes no criterio
   - Piorou: mais refacoes no criterio
4. Identificar pontos fortes do designer (criterios sem refacao)
5. Formatar relatorio individual

## Regras

- Alertar gestor quando designer atinge 3+ refacoes na semana
- Identificar designers referencia (0 refacoes) para mentoria
- Periodo padrao: ultimos 30 dias
- Relatorio deve ser construtivo (incluir pontos fortes)
