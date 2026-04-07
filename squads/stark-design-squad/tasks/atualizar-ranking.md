---
task: Atualizar Ranking
responsavel: "@qa-qualidade"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Posts com avaliacoes do mes
  - Dados de tripla validacao
Saida: |
  - Ranking mensal atualizado no Google Sheets
Checklist:
  - "[ ] Coletar todos os posts avaliados no mes"
  - "[ ] Verificar tripla validacao (QA + Cliente + Desempenho)"
  - "[ ] Classificar: Premium (3/3) ou Validado (2/3)"
  - "[ ] Atualizar planilha de ranking"
  - "[ ] Destacar posts Premium como referencia"
---

# *ranking

Atualiza o ranking mensal de posts com base na tripla validacao: QA + Aprovacao do Cliente + Desempenho.

## Uso

```
*ranking --mes "marco"
*ranking "Atualizar ranking de fevereiro 2026"
```

## Fluxo

1. Coletar todos os posts avaliados no mes de referencia
2. Para cada post, verificar tripla validacao:
   - QA aprovou (nota >= 7.0)
   - Cliente aprovou (via ClickUp ou email)
   - Bom desempenho (engagement rate acima da media do cliente)
3. Classificar:
   - **Premium**: 3/3 criterios atendidos
   - **Validado**: 2/3 criterios atendidos
4. Atualizar planilha de ranking no Google Sheets
5. Destacar posts Premium como referencia para o time

## Regras

- Tripla validacao obrigatoria para classificacao Premium
- QA minimo: nota 7.0
- Desempenho: engagement_rate > media rolling do cliente (30 posts)
- Posts Premium servem de referencia para futuras criacoes
- Ranking ordenado por nota geral (maior primeiro)
