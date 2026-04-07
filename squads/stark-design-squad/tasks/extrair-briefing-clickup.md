---
task: Extrair Briefing ClickUp
responsavel: "@pesquisador-ref"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Task ID do ClickUp (ex: 86age325k)
  - Incluir subtasks (opcional, default: false)
Saida: |
  - Briefing estruturado com todos os assets extraidos
  - Links embarcados (Instagram, Drive, Figma) identificados e acessiveis
  - Imagens do briefing baixadas localmente
  - JSON com briefing completo
Checklist:
  - "[ ] Buscar task via ClickUp MCP"
  - "[ ] Extrair description (text_content)"
  - "[ ] Buscar links embutidos via API REST (markdown_description)"
  - "[ ] Identificar e categorizar links (Instagram, Drive, Figma, outros)"
  - "[ ] Buscar anexos da task e da task-pai"
  - "[ ] Baixar imagens encontradas para /tmp/briefing-{task_id}/"
  - "[ ] Montar JSON estruturado do briefing"
---

# *extrair-briefing

Extrai o briefing completo de uma task do ClickUp, incluindo links embutidos no rich text e imagens inline que a API padrao nao retorna.

## Problema

A API do ClickUp retorna `text_content` e `description` como texto plano, perdendo:
- Hyperlinks embutidos (Instagram, Drive, Figma)
- Imagens inline coladas no editor rich text
- Formatacao rica (bold, listas, etc.)

Esta task resolve esse gap extraindo o maximo de informacao possivel.

## Uso

```
*extrair-briefing 86age325k
*extrair-briefing 86age325k --subtasks
*extrair-briefing --task-url "https://app.clickup.com/t/86age325k"
```

## Fluxo

1. **Buscar task via MCP**: `clickup_get_task` com `detail_level=detailed`
2. **Extrair campos basicos**:
   - `name`: nome da task
   - `text_content`: descricao em texto plano
   - `assignees`: responsaveis
   - `custom_fields`: campos personalizados (CTA, Etapa do Funil, Procedimento, etc.)
   - `due_date`: prazo
   - `priority`: prioridade
   - `status`: status atual
   - `parent`: task-pai (para contexto de semana/cliente)
3. **Buscar links embutidos**:
   - Tentar ClickUp REST API via Bash/curl para obter `description` em formato markdown
   - Regex para extrair URLs: `https?://[^\s\)]+`
   - Categorizar links encontrados:
     - `instagram.com/p/` → referencia Instagram
     - `drive.google.com` ou `docs.google.com` → arquivo/pasta Drive
     - `figma.com/design/` → referencia Figma
     - Outros → link generico
4. **Buscar anexos**:
   - Verificar `attachments[]` da task
   - Verificar `attachments[]` da task-pai (se existir `parent`)
   - Verificar comentarios da task por anexos
5. **Buscar imagens inline**:
   - Imagens coladas no editor ClickUp ficam em CDN do ClickUp
   - Tentar extrair URLs de imagem do campo `description` (formato markdown: `![](url)`)
   - Se encontradas, baixar para `/tmp/briefing-{task_id}/`
6. **Montar briefing estruturado**:
   ```json
   {
     "task_id": "86age325k",
     "task_name": "06/04 (Segunda) - Criativo: Estatico | Dr Thiago Souza",
     "client": "Dr Thiago Souza",
     "assignee": "Humberto Sales",
     "due_date": "2026-04-06",
     "status": "a ser feito",
     "priority": "urgent",
     "copy": {
       "image_text": "Voce ama seus filhos...",
       "caption": "Nao tem problema nenhum em admitir isso..."
     },
     "custom_fields": {
       "cta": null,
       "etapa_funil": null,
       "procedimento": null,
       "formato": "Post"
     },
     "references": {
       "instagram": [
         {
           "url": "https://www.instagram.com/p/DVYq34GmrBP/",
           "type": "post",
           "extracted": false,
           "reason": "post removido/privado"
         }
       ],
       "drive": [],
       "figma": [],
       "other": []
     },
     "attachments": [],
     "inline_images": [],
     "local_files": ["/tmp/briefing-86age325k/"]
   }
   ```
7. **Salvar output**: `/tmp/briefing-{task_id}/briefing.json`

## Regras

- SEMPRE buscar a task-pai para contexto (cliente, semana)
- SEMPRE verificar anexos em task + task-pai + comentarios
- Links do Instagram encontrados: tentar extrair via `*buscar-referencias --fonte instagram`
- Links do Drive encontrados: tentar baixar via Google Drive API (credentials.json)
- Links do Figma encontrados: registrar para uso pelo designer-figma
- Se nenhum link/imagem encontrado: reportar claramente (nao inventar)
- Output SEMPRE em JSON estruturado
- Imagens baixadas em `/tmp/briefing-{task_id}/`

## Integracao com Outros Agentes

| Agente | Quando |
|--------|--------|
| `pesquisador-ref` | Links Instagram encontrados → `*buscar-referencias --fonte instagram` |
| `designer-figma` | Links Figma encontrados → referenciar no design |
| `brand-guardian` | Cliente identificado → consultar identidade visual |
| `orquestrador` | Briefing completo → delegar criacao |

## Limitacoes Conhecidas

1. **Imagens inline do ClickUp**: A API nao expoe imagens coladas no editor rich text. Workaround: tentar extrair do campo `description` em formato markdown
2. **Links em rich text**: A API retorna `text_content` sem hyperlinks. Workaround: buscar via REST API o campo `description` que pode conter markdown com links
3. **Posts Instagram privados/removidos**: Apify pode nao conseguir acessar. Reportar e sugerir screenshot manual
