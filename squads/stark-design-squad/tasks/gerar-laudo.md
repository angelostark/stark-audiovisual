---
task: Gerar Laudo
responsavel: "@qa-qualidade"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Resultado da avaliacao (notas por criterio)
Saida: |
  - Laudo formatado pronto para postar no ClickUp
Checklist:
  - "[ ] Formatar nota geral e por criterio"
  - "[ ] Listar pontos positivos"
  - "[ ] Listar regras quebradas com descricao"
  - "[ ] Definir status final"
  - "[ ] Descrever proximos passos para o designer"
  - "[ ] Postar laudo no chat da subtarefa"
---

# *laudo

Gera laudo formatado de avaliacao QA para postar no ClickUp com notas, regras quebradas e proximos passos.

## Uso

```
*laudo
*laudo --post "Carrossel Dra. Camila Rino"
```

## Fluxo

1. Coletar resultado da avaliacao (notas por criterio)
2. Formatar laudo no padrao:
   ```
   Nota geral: X/10
   Por criterio: [criterio]: X/10
   Pontos positivos: ...
   Regras quebradas: [lista das regras violadas]
   Status: APROVADO / APROVADO COM RESSALVAS / REPROVADO
   Proximos passos: [o que o designer deve ajustar]
   ```
3. Postar laudo no chat da subtarefa no ClickUp

## Regras

- Sempre incluir nota geral e por criterio
- Sempre listar pontos positivos (mesmo em reprovacoes)
- Regras quebradas devem ter descricao clara do problema
- Proximos passos devem ser especificos e acionaveis
- Status deve seguir a escala: Premium (9-10), Aprovado (7-8), Ressalvas (5-6), Reprovado (<5)
