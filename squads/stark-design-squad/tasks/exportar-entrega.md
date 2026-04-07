---
task: Exportar Entrega
responsavel: "@orquestrador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Frame do Figma (link ou nome)
  - Nome do cliente
Saida: |
  - PNGs no Google Drive (pasta do cliente)
  - Comentario na subtarefa do ClickUp com link
  - Responsavel da tarefa mae notificado
  - Status da subtarefa: edicao concluida
Checklist:
  - "[ ] Localizar frame no Figma"
  - "[ ] Extrair data e nome do Drive do nome do frame"
  - "[ ] Identificar tipo (estatico/carrossel)"
  - "[ ] Exportar PNGs"
  - "[ ] Upload para Drive via upload_drive.py"
  - "[ ] Buscar subtarefa no ClickUp"
  - "[ ] Encontrar responsavel da tarefa mae"
  - "[ ] Postar comentario com link do Drive"
  - "[ ] Atualizar status para edicao concluida"
---

# *exportar-entrega

Exporta frames do Figma como PNGs, faz upload para o Drive do cliente e registra a entrega no ClickUp. Reutiliza o skill `figma-export-para-drive`.

## Uso

```
*exportar-entrega "Frame Dra. Camila - Carrossel Rino"
*exportar-entrega --frame "link_do_figma" --cliente "Dr. Cadu"
```

## Fluxo

1. Localizar frame no Figma (por link ou nome)
2. Extrair metadados do nome do frame (data, cliente, tipo)
3. Identificar tipo: estatico (1 PNG) ou carrossel (multiplos PNGs)
4. Exportar PNGs via Figma MCP
5. Upload para Drive na pasta correta via `upload_drive.py`
6. Buscar subtarefa correspondente no ClickUp
7. Identificar responsavel da tarefa mae
8. Postar comentario no ClickUp com link do Drive
9. Atualizar status da subtarefa para "edicao concluida"

## Regras

- Nunca exportar fora da estrutura de pastas padrao do cliente
- Resolucao: 1080x1350 (feed) ou 1080x1920 (stories/reels)
- Formato: PNG para estaticos, JPG para fotografias
- Naming: [cliente]-[tipo]-[AAAAMMDD]-v[numero]
- Sempre notificar responsavel da tarefa mae apos upload
