---
task: Criar Variacao A/B
responsavel: "@construtor-capa-reels"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Capa base aprovada ou em revisao
Saida: |
  - 2 variacoes A/B para teste de performance
Checklist:
  - "[ ] Manter identidade do cliente consistente"
  - "[ ] Variacao A: alterar CTA (texto ou posicao)"
  - "[ ] Variacao B: alterar cor dominante"
  - "[ ] Opcionalmente: variar posicao do texto principal"
  - "[ ] Verificar que ambas variacoes seguem regras Stark"
  - "[ ] Enviar para QA"
---

# *criar-variacao-ab

Gera variacoes A/B de uma capa existente para teste de performance no Instagram.

## Uso

```
*criar-variacao-ab --base "Capa Dr. Cadu Rino"
*criar-variacao-ab "Variacoes para capa de lipo Dra. Camila"
```

## Fluxo

1. Acessar capa base (aprovada ou em revisao)
2. Criar Variacao A: alterar CTA (texto ou posicao)
3. Criar Variacao B: alterar cor dominante
4. Opcionalmente: variar posicao do texto principal
5. Verificar que ambas variacoes seguem regras Stark
6. Manter identidade do cliente consistente entre variacoes
7. Enviar ambas para QA

## Regras

- Identidade do cliente deve ser consistente entre variacoes
- Variar apenas 1 elemento por variacao para teste valido
- Checklist A/B:
  - Variar CTA (texto ou posicao)
  - Variar cor dominante
  - Variar posicao do texto principal
- Ambas variacoes devem seguir todas as regras Stark
- Sempre enviar para QA antes de finalizar
