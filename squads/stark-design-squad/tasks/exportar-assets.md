---
task: Exportar Assets
responsavel: "@designer-figma"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Frame(s) finalizados no Figma
Saida: |
  - PNGs exportados em /tmp/figma_exports/
  - Upload feito para Drive
Checklist:
  - "[ ] Verificar resolucao (1080x1350 ou 1080x1920)"
  - "[ ] Exportar como PNG (estaticos) ou JPG (fotografias)"
  - "[ ] Nomear arquivos corretamente"
  - "[ ] Upload para Drive via upload_drive.py"
---

# *exportar-assets

Exporta assets finalizados do Figma nos formatos e resolucoes corretas e faz upload para o Drive do cliente.

## Uso

```
*exportar-assets --frame "link_do_figma"
*exportar-assets "Exportar carrossel Dra. Camila marco"
```

## Fluxo

1. Localizar frame(s) no Figma
2. Verificar resolucao correta:
   - Feed: 1080x1350px
   - Stories/Reels: 1080x1920px
3. Exportar nos formatos corretos:
   - Estaticos/layouts: PNG
   - Fotografias: JPG
4. Nomear arquivos: [cliente]-[tipo]-[AAAAMMDD]-v[numero]
5. Salvar em /tmp/figma_exports/
6. Upload para Drive via upload_drive.py na pasta do cliente

## Regras

- Nunca exportar fora da estrutura de pastas padrao
- Resolucao feed: 1080x1350px | Stories: 1080x1920px
- PNG para estaticos, JPG para fotografias
- Naming: [cliente]-[tipo]-[AAAAMMDD]-v[numero]
- Verificar que nao ha artefatos visuais antes de exportar
