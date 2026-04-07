---
task: Criar Layout
responsavel: "@designer-figma"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Briefing com descricao do post
  - Referencias visuais (do Pesquisador Ref)
  - Brand guidelines (do Brand Guardian)
Saida: |
  - Frame no Figma nomeado e organizado
  - Seguindo identidade visual do cliente
Checklist:
  - "[ ] Consultar Brand Guardian para paleta/fontes/fotos"
  - "[ ] Consultar Pesquisador Ref para referencias (se aplicavel)"
  - "[ ] Verificar briefing aprovado no ClickUp"
  - "[ ] Criar frame no Figma com naming correto"
  - "[ ] Aplicar identidade visual do cliente"
  - "[ ] Verificar elementos obrigatorios (capa)"
  - "[ ] Organizar na pasta correta do Figma"
  - "[ ] Enviar para QA"
---

# *criar-layout

Cria um novo layout no Figma a partir de briefing, aplicando identidade visual do cliente e seguindo o padrao Stark.

## Uso

```
*criar-layout --cliente "Dra. Camila" --tipo "carrossel" --tema "rinoplastia"
*criar-layout "Estatico promocional para Dr. Cadu"
```

## Fluxo

1. Consultar Brand Guardian para paleta, fontes e fotos do cliente
2. Consultar Pesquisador Ref para referencias visuais (se aplicavel)
3. Verificar briefing aprovado no ClickUp
4. Criar frame no Figma com naming: [cliente]-[tipo]-[AAAAMMDD]-v[numero]
5. Aplicar identidade visual: cores, tipografia, logo
6. Verificar elementos obrigatorios da capa (logo, titulo, CTA, foto)
7. Organizar na pasta correta do Figma
8. Enviar para QA de Qualidade para avaliacao

## Regras

- Nunca alterar arquivos de outros clientes
- Consultar Brand Guardian ANTES de iniciar criacao
- Naming: [cliente]-[tipo]-[AAAAMMDD]-v[numero]
- Elementos obrigatorios: LOGO/ICON, Titulo+Subtitulo, CTA, imagem de apoio, foto Doctor(a)
- Toda entrega passa pelo QA antes de ser finalizada
