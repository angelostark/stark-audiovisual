---
task: Criar Landing Page
responsavel: "@web-designer-lp"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Briefing + referencias
  - Brand guidelines do cliente
  - Biblioteca de componentes existente
Saida: |
  - LP completa (mobile + desktop)
  - Componentes nomeados no padrao Atomic
Checklist:
  - "[ ] Consultar Brand Guardian"
  - "[ ] Listar atomos/moleculas disponiveis (*listar-atomos)"
  - "[ ] Identificar componentes reutilizaveis"
  - "[ ] Criar atomos faltantes"
  - "[ ] Compor moleculas necessarias"
  - "[ ] Montar organismos (hero, depoimentos, etc.)"
  - "[ ] Criar template da LP"
  - "[ ] Preencher com conteudo real (pagina)"
  - "[ ] Verificar responsividade (mobile + desktop)"
  - "[ ] Verificar acessibilidade WCAG"
  - "[ ] Organizar na estrutura 01-Atomos/ a 05-Paginas/"
  - "[ ] Enviar para QA"
---

# *criar-lp

Constroi uma landing page completa usando Atomic Design — do atomo ate a pagina final com conteudo real do cliente.

## Uso

```
*criar-lp --cliente "Clinica Bella Vita" --tipo "captacao" --ref "link_referencia"
*criar-lp "LP para campanha de lipo do Dr. Cadu"
```

## Fluxo

1. Consultar Brand Guardian para identidade visual do cliente
2. Listar componentes existentes (*listar-atomos)
3. Identificar quais atomos/moleculas podem ser reutilizados
4. Criar atomos faltantes (botoes, inputs, badges, tipografia)
5. Compor moleculas (cards, search bars, campos com label)
6. Montar organismos complexos (hero, header, depoimentos, formulario)
7. Criar template da LP com placeholders
8. Preencher com conteudo real do cliente (pagina final)
9. Verificar responsividade: mobile + desktop
10. Verificar acessibilidade WCAG
11. Organizar tudo na estrutura de pastas Atomic
12. Enviar para QA

## Regras

- Todo componente classificado no nivel Atomic correto
- Reutilizar atomos/moleculas existentes antes de criar novos
- Nomenclatura: [nivel]-[tipo]-[cliente]-[variante]
- Responsivo obrigatorio: mobile + desktop
- Acessibilidade WCAG desde o inicio
- Estrutura de pastas: 01-Atomos/ → 02-Moleculas/ → 03-Organismos/ → 04-Templates/ → 05-Paginas/
