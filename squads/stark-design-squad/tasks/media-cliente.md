---
task: Media Cliente
responsavel: "@analytics-posts"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Nome do cliente
  - Periodo (30/60/90 dias)
Saida: |
  - Media de engagement rate no periodo
  - Tendencia (subindo/descendo/estavel)
  - Top 3 posts do periodo
Checklist:
  - "[ ] Filtrar posts do cliente no periodo"
  - "[ ] Calcular media de engagement rate"
  - "[ ] Calcular tendencia (comparar com periodo anterior)"
  - "[ ] Identificar top 3 posts"
  - "[ ] Retornar relatorio formatado"
---

# *media-cliente

Calcula a media de engagement de um cliente em um periodo e identifica tendencias de desempenho.

## Uso

```
*media-cliente "Dra. Camila" --periodo "30 dias"
*media-cliente --cliente "Dr. Cadu" --periodo "90 dias"
*media-cliente "Bella Vita ultimos 60 dias"
```

## Fluxo

1. Filtrar posts do cliente no periodo solicitado (Google Sheets)
2. Calcular media de engagement rate do periodo
3. Calcular tendencia comparando com periodo anterior:
   - Subindo: media atual > media anterior
   - Descendo: media atual < media anterior
   - Estavel: variacao < 5%
4. Identificar top 3 posts do periodo (maior engagement rate)
5. Retornar relatorio formatado

## Regras

- Periodos validos: 30, 60 ou 90 dias
- Tendencia calculada comparando periodo atual vs anterior de mesma duracao
- Top 3 posts ordenados por engagement rate (maior primeiro)
- Se menos de 5 posts no periodo: alertar amostra insuficiente
