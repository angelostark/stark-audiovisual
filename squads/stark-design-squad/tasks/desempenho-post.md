---
task: Desempenho Post
responsavel: "@analytics-posts"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Post ID ou identificador
  - Metricas do post (likes, comments, shares, reach, saves)
Saida: |
  - Engagement rate calculado
  - Comparacao com media do cliente
  - Status: acima/abaixo da media
Checklist:
  - "[ ] Buscar post na planilha de metricas"
  - "[ ] Calcular engagement rate"
  - "[ ] Buscar media rolling do cliente (ultimos 30 posts)"
  - "[ ] Comparar e classificar"
  - "[ ] Atualizar campo performance_status"
---

# *desempenho-post

Calcula o engagement rate de um post e compara com a media historica do cliente.

## Uso

```
*desempenho-post --post "POST-001" --likes 250 --comments 30 --shares 15 --reach 5000 --saves 45
*desempenho-post "Verificar desempenho do ultimo post da Dra. Camila"
```

## Fluxo

1. Buscar post na planilha de metricas (Google Sheets)
2. Calcular engagement rate: (likes + comments + shares + saves) / reach * 100
3. Buscar media rolling do cliente (ultimos 30 posts)
4. Comparar engagement rate com media:
   - Acima da media: bom desempenho
   - Abaixo da media: desempenho insuficiente
5. Atualizar campo performance_status na planilha

## Regras

- Formula: engagement_rate = (likes + comments + shares + saves) / reach * 100
- Media do cliente: rolling average dos ultimos 30 posts
- Bom desempenho: engagement_rate > media do cliente
- Atualizar planilha apos cada calculo
