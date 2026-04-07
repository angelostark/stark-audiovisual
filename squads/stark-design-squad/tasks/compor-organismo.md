---
task: Compor Organismo
responsavel: "@web-designer-lp"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Tipo de organismo desejado (hero, depoimentos, etc.)
  - Moleculas/atomos a combinar
  - Cliente + variante
Saida: |
  - Organismo composto e nomeado
  - Mapeamento de dependencias (quais atomos/moleculas usa)
Checklist:
  - "[ ] Verificar moleculas/atomos necessarios existem"
  - "[ ] Criar faltantes se necessario"
  - "[ ] Compor organismo combinando componentes"
  - "[ ] Nomear: organismo-[tipo]-[cliente]-[variante]"
  - "[ ] Registrar dependencias"
  - "[ ] Testar responsividade"
---

# *compor-organismo

Compoe um organismo complexo (hero, header, secao depoimentos, formulario) combinando moleculas e atomos existentes.

## Uso

```
*compor-organismo --tipo "hero" --cliente "FitLife" --variante "escuro"
*compor-organismo "Secao depoimentos grid para Clinica Bella"
```

## Fluxo

1. Identificar tipo de organismo desejado
2. Listar moleculas e atomos necessarios
3. Verificar quais ja existem na biblioteca
4. Criar componentes faltantes se necessario
5. Compor organismo combinando os componentes
6. Nomear: organismo-[tipo]-[cliente]-[variante]
7. Registrar mapa de dependencias (quais atomos/moleculas compoe o organismo)
8. Testar responsividade (mobile + desktop)

## Regras

- Sempre verificar componentes existentes antes de criar novos
- Nomenclatura: organismo-[tipo]-[cliente]-[variante]
- Registrar dependencias para rastreabilidade
- Responsivo obrigatorio: mobile + desktop
- Seguir paleta e tipografia do Brand Guardian
