---
task: Refacoes Semana
responsavel: "@monitor-refacoes"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Periodo (semana ou mes)
Saida: |
  - Resumo de refacoes: total, por motivo, por designer, por cliente
  - Comparacao com periodo anterior
Checklist:
  - "[ ] Buscar laudos QA com veredito Reprovado ou Ressalvas no periodo"
  - "[ ] Agrupar por motivo de refacao (criterio mais falhado)"
  - "[ ] Agrupar por designer responsavel"
  - "[ ] Agrupar por cliente"
  - "[ ] Comparar com periodo anterior (melhoria/piora)"
  - "[ ] Gerar resumo formatado"
---

# *refacoes-semana

Gera resumo de refacoes da semana/mes agrupado por motivo, designer e cliente, com comparacao historica.

## Uso

```
*refacoes-semana
*refacoes-semana --periodo "mes"
*refacoes-semana "Resumo de refacoes da semana 24/03"
```

## Fluxo

1. Buscar laudos QA com veredito Reprovado ou Aprovado com Ressalvas no periodo
2. Agrupar por motivo principal de refacao (criterio QA mais falhado)
3. Agrupar por designer responsavel
4. Agrupar por cliente
5. Comparar com periodo anterior:
   - Melhoria: menos refacoes que periodo anterior
   - Piora: mais refacoes que periodo anterior
   - Estavel: variacao < 10%
6. Gerar resumo formatado

## Regras

- Coletar dados de TODOS os laudos QA com veredito != Aprovado Premium/Aprovado
- Periodo padrao: semana atual
- Alertar gestor quando total de refacoes aumentar >20% vs periodo anterior
- Incluir taxa de refacao: refacoes / total entregas * 100
