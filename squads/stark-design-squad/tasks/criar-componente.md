---
task: Criar Componente
responsavel: "@web-designer-lp"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Tipo do componente
  - Cliente + variante
  - Nivel Atomic (atomo/molecula/organismo)
Saida: |
  - Componente nomeado e categorizado
  - Documentacao de uso
Checklist:
  - "[ ] Classificar nivel Atomic correto"
  - "[ ] Verificar se componente similar ja existe"
  - "[ ] Criar com naming: [nivel]-[tipo]-[cliente]-[variante]"
  - "[ ] Organizar na pasta correta (01-Atomos/ a 03-Organismos/)"
  - "[ ] Documentar props e variantes"
---

# *criar-componente

Cria um componente individual no sistema Atomic Design, classificado no nivel correto e documentado para reuso.

## Uso

```
*criar-componente --nivel "atomo" --tipo "botao" --variante "primary-v1"
*criar-componente --nivel "molecula" --tipo "card-preco" --cliente "Bella Vita"
*criar-componente "Organismo hero escuro para FitLife"
```

## Fluxo

1. Classificar nivel Atomic correto (atomo, molecula, organismo)
2. Verificar se componente similar ja existe na biblioteca
3. Se existir similar: avaliar se pode ser variante ou precisa ser novo
4. Criar componente com naming padrao:
   - Atomos: atomo-[tipo]-[variante] (ex: atomo-botao-primary-v1)
   - Moleculas: molecula-[tipo]-[cliente]-[variante] (ex: molecula-card-preco-dentalPrime-v1)
   - Organismos: organismo-[tipo]-[cliente]-[variante] (ex: organismo-hero-fitlife-escuro)
5. Organizar na pasta correta do Figma
6. Documentar props e variantes para facilitar reuso

## Regras

- Todo componente deve ser classificado no nivel Atomic correto
- Reutilizar existentes antes de criar novos
- Nomenclatura: [nivel]-[tipo]-[cliente]-[variante]
- Documentar sempre para facilitar reuso pelo time
