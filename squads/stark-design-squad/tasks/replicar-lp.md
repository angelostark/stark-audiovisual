---
task: Replicar Landing Page
responsavel: "@web-designer-lp"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - LP existente de referencia
  - Novo cliente/campanha
Saida: |
  - LP replicada com identidade adaptada
  - Componentes reutilizados por nivel Atomic
Checklist:
  - "[ ] Analisar LP de referencia por nivel Atomic"
  - "[ ] Identificar atomos/moleculas reutilizaveis"
  - "[ ] Adaptar organismos com nova identidade"
  - "[ ] Criar novo template se necessario"
  - "[ ] Preencher com conteudo do novo cliente"
  - "[ ] Verificar responsividade e acessibilidade"
  - "[ ] Enviar para QA"
---

# *replicar-lp

Replica uma landing page existente para novo cliente/campanha, reutilizando componentes Atomic e adaptando identidade visual.

## Uso

```
*replicar-lp --ref "LP Bella Vita Marco" --destino "Clinica Renova"
*replicar-lp "Replicar LP do Dr. Cadu para Dra. Camila"
```

## Fluxo

1. Analisar LP de referencia decompondo por nivel Atomic
2. Identificar atomos e moleculas reutilizaveis (genericos)
3. Consultar Brand Guardian do novo cliente
4. Adaptar organismos com nova identidade (cores, fontes, logo)
5. Criar novo template se a estrutura precisar mudar
6. Preencher com conteudo real do novo cliente
7. Verificar responsividade (mobile + desktop) e acessibilidade WCAG
8. Enviar para QA

## Regras

- Maximizar reuso de componentes existentes
- Nunca alterar a LP original de referencia
- Nomenclatura: [nivel]-[tipo]-[cliente]-[variante]
- Responsivo obrigatorio: mobile + desktop
- Acessibilidade WCAG obrigatoria
