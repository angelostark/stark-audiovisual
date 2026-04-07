---
task: Buscar Referencias
responsavel: "@pesquisador-ref"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Nicho do cliente (ex: cirurgia plastica)
  - Tipo de post (carrossel, estatico, capa, LP)
  - Estilo desejado (opcional)
  - Fonte especifica (opcional): behance, dribbble, pinterest, instagram
  - URL direta (opcional): link de post Instagram para extração
Saida: |
  - 5-10 referencias visuais em JSON
  - Cada referencia com URL, tags de estilo e relevance_score
  - Para Instagram: imagens do post, caption, hashtags, engagement hints
Checklist:
  - "[ ] Buscar no moodboard Stark (base)"
  - "[ ] Buscar em Behance/Dribbble/Pinterest via Web Search"
  - "[ ] Se --fonte instagram: buscar via Apify Instagram Scraper (Docker MCP)"
  - "[ ] Filtrar por relevancia ao nicho"
  - "[ ] Priorizar referencias dos ultimos 6 meses"
  - "[ ] Retornar 5-10 resultados com thumbnails"
  - "[ ] Incluir tags de estilo"
---

# *buscar-referencias

Busca referencias visuais por nicho, tipo de post e estilo para alimentar designers com inspiracao fresca.

## Uso

```
*buscar-referencias --nicho "cirurgia plastica" --tipo "carrossel" --estilo "minimal"
*buscar-referencias "Referencias de capas de reels para odontologia"
*buscar-referencias --nicho "estetica" --tipo "LP"
*buscar-referencias --fonte instagram --url "instagram.com/p/ABC123/"
*buscar-referencias --fonte instagram --perfil "dr.thiagosouza" --nicho "mastopexia"
```

## Fluxo

1. Consultar moodboard Stark como base de referencia
2. Determinar fonte de busca:
   - **Default**: Behance, Dribbble, Pinterest via Web Search
   - **Instagram** (`--fonte instagram`): via Apify MCP (Docker Gateway)
3. **Fluxo Instagram** (quando `--fonte instagram`):
   a. Se `--url` fornecida: extrair post específico via Apify Instagram Post Scraper
   b. Se `--perfil` fornecido: buscar posts recentes do perfil
   c. Extrair: imagens, caption, hashtags, data, engagement (likes/comments)
   d. Salvar imagens em `/tmp/ref-instagram/` para uso local
4. Filtrar por relevancia ao nicho do cliente
5. Priorizar referencias dos ultimos 6 meses
6. Retornar 5-10 resultados em formato JSON:
   ```json
   {
     "url": "string",
     "thumbnail_url": "string",
     "source": "behance|dribbble|pinterest|instagram|other",
     "style_tags": ["minimal", "bold", "organic"],
     "relevance_score": 0.85,
     "description": "string",
     "instagram_data": {
       "caption": "string (se fonte=instagram)",
       "hashtags": ["tag1", "tag2"],
       "image_urls": ["url1", "url2"],
       "local_images": ["/tmp/ref-instagram/img1.jpg"]
     }
   }
   ```
7. Incluir tags de estilo para facilitar filtragem

## Fluxo Instagram (detalhado)

Quando `--fonte instagram` é usado, o agente deve:

1. **Buscar Actor**: `search-actors` com query "instagram post scraper" ou "instagram profile scraper"
2. **Executar Actor**: `call-actor` com a URL ou perfil fornecido
3. **Obter resultados**: `get-actor-output` para extrair dados do post/perfil
4. **Processar**: Mapear dados do Instagram para o schema JSON de referências
5. **Fallback**: Se Apify falhar, tentar WebFetch no embed (`/p/{id}/embed/`)
6. **Fallback 2**: Se tudo falhar, reportar e sugerir screenshot manual

### Acesso Apify (via Docker Gateway)

```
mcp__docker-gateway__search-actors         # Buscar Actor de Instagram
mcp__docker-gateway__call-actor            # Executar scraping
mcp__docker-gateway__get-actor-output      # Obter resultados
```

## Regras

- Sempre incluir moodboard Stark como referencia base
- Retornar entre 5-10 referencias por busca
- Incluir tags de estilo para facilitar filtragem
- Priorizar referencias recentes (ultimos 6 meses)
- Variar fontes: Behance, Dribbble, Pinterest, Instagram
- Instagram: SEMPRE usar Apify via Docker MCP (nunca scraping direto)
- Instagram: salvar imagens localmente em `/tmp/ref-instagram/` para acesso offline
- Instagram: respeitar rate limits do Apify (max 1 Actor run por busca)
