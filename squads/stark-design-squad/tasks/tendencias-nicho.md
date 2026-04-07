---
task: Tendencias Nicho
responsavel: "@pesquisador-ref"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Nicho (ex: clinica de estetica, odontologia)
Saida: |
  - Relatorio de tendencias visuais atuais
  - Paletas em alta, estilos dominantes, referencias
Checklist:
  - "[ ] Pesquisar tendencias atuais no nicho"
  - "[ ] Identificar paletas em alta"
  - "[ ] Identificar estilos de layout dominantes"
  - "[ ] Comparar com ultimos layouts do squad"
  - "[ ] Gerar relatorio com recomendacoes"
---

# *tendencias-nicho

Pesquisa tendencias visuais atuais por nicho para manter o squad atualizado com o mercado.

## Uso

```
*tendencias-nicho "cirurgia plastica"
*tendencias-nicho --nicho "odontologia"
*tendencias-nicho "estetica facial"
```

## Fluxo

1. Pesquisar tendencias visuais atuais no nicho via Web Search
2. Identificar paletas de cores em alta no segmento
3. Identificar estilos de layout dominantes (minimal, bold, organic, etc.)
4. Comparar com ultimos layouts produzidos pelo squad
5. Gerar relatorio com:
   - Paletas em alta (com hex codes)
   - Estilos dominantes
   - Referencias visuais (links)
   - Recomendacoes para o squad

## Regras

- Focar em tendencias dos ultimos 6 meses
- Incluir referencias visuais concretas (links)
- Comparar com producao recente do squad para identificar gaps
- Relatorio deve ser acionavel (recomendacoes claras)
