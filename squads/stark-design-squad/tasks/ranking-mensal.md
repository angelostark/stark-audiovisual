---
task: Ranking Mensal
responsavel: "@analytics-posts"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Mes de referencia
Saida: |
  - Ranking completo de posts com tripla validacao
  - Posts Premium destacados
  - Estatisticas por designer e cliente
Checklist:
  - "[ ] Coletar posts do mes com notas QA"
  - "[ ] Verificar aprovacao do cliente (manual)"
  - "[ ] Verificar desempenho (engagement vs media)"
  - "[ ] Aplicar tripla validacao"
  - "[ ] Classificar: Premium (3/3) ou Validado (2/3)"
  - "[ ] Gerar ranking ordenado por nota"
  - "[ ] Calcular estatisticas por designer"
  - "[ ] Atualizar planilha de ranking"
---

# *ranking-mensal

Gera o ranking mensal completo de posts com tripla validacao e estatisticas por designer/cliente.

## Uso

```
*ranking-mensal --mes "marco"
*ranking-mensal "Ranking de fevereiro 2026"
```

## Fluxo

1. Coletar todos os posts do mes com notas QA (Google Sheets)
2. Para cada post, verificar tripla validacao:
   - QA aprovou (nota >= 7.0)
   - Cliente aprovou (verificacao manual via ClickUp)
   - Bom desempenho (engagement rate > media do cliente)
3. Classificar:
   - **Premium (3/3)**: todas as validacoes verdadeiras
   - **Validado (2/3)**: pelo menos 2 validacoes
4. Gerar ranking ordenado por nota geral (maior primeiro)
5. Calcular estatisticas por designer: total posts, % Premium, media QA
6. Calcular estatisticas por cliente: total posts, engagement medio
7. Atualizar planilha de ranking no Google Sheets

## Regras

- Tripla validacao: qa_score >= 7 AND client_approved AND bom_desempenho
- Premium: todas as 3 validacoes verdadeiras
- Posts Premium servem de referencia para futuras criacoes
- Ranking ordenado por nota geral (maior primeiro)
- Atualizar planilha apos geracao
