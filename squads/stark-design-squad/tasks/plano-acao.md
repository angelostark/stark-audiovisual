---
task: Plano de Acao
responsavel: "@monitor-refacoes"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Dados de refacoes do periodo
  - Laudos QA detalhados
Saida: |
  - Plano de acao com feedback individual por designer
  - Sugestoes de melhoria por cliente
  - Metas para o proximo periodo
  - Destaque de designers referencia
Checklist:
  - "[ ] Analisar padroes de erro por designer"
  - "[ ] Gerar feedback individual especifico"
  - "[ ] Identificar mentoria possivel (designer forte -> designer fraco)"
  - "[ ] Sugerir acoes para clientes problematicos"
  - "[ ] Definir metas quantitativas (ex: reduzir refacoes em 30%)"
  - "[ ] Destacar designers com 0 refacoes como referencia"
  - "[ ] Formatar plano pronto para apresentar na daily"
---

# *plano-acao

Gera plano de acao semanal com feedback individual, sugestoes de melhoria, metas e destaques de referencia.

## Uso

```
*plano-acao
*plano-acao --periodo "semana 24/03"
*plano-acao "Plano de acao para o time de design"
```

## Fluxo

1. Coletar dados de refacoes do periodo (via *refacoes-semana)
2. Analisar padroes de erro por designer:
   - Quais criterios QA mais falham por designer
   - Quais clientes geram mais refacoes
3. Gerar feedback individual especifico e construtivo:
   - Pontos fortes identificados
   - Criterios a melhorar com exemplos concretos
   - Acoes especificas para a proxima semana
4. Identificar oportunidades de mentoria:
   - Designer forte em criterio X → ajudar designer fraco em X
5. Sugerir acoes para clientes problematicos:
   - Melhorar briefing, atualizar Brand Guardian, reuniao de alinhamento
6. Definir metas quantitativas para proximo periodo:
   - Ex: reduzir refacoes em 30%, zero reprovacoes por regra Stark
7. Destacar designers com 0 refacoes como referencia
8. Formatar plano pronto para apresentar na daily

## Regras

- Plano de acao semanal e obrigatorio
- Feedback deve ser construtivo: sempre incluir pontos fortes
- Metas devem ser quantitativas e atingiveis
- Designers referencia (0 refacoes) devem ser destacados publicamente
- Formato pronto para apresentacao na daily do time
- Alertar gestor quando designer atinge 3+ refacoes na semana
