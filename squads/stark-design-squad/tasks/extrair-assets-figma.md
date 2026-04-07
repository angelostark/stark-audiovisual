# Task: Extrair Assets do Figma

## Metadata
- **Agent:** web-designer-lp
- **Command:** `*extrair-assets`
- **Args:** `{figma_url|frame_id} {cliente}`

## Descrição
Coleta todos os assets de um frame/página do Figma, renomeia seguindo o padrão Atomic Design e organiza na estrutura correta por nível.

## Pré-condições
- [ ] URL ou ID do frame Figma fornecido
- [ ] Nome do cliente informado
- [ ] Brand Guardian consultado para identificar logos e assets da marca

## Workflow

### STEP 1 — Ler estrutura do Figma
1. Acessar frame via Figma MCP (`get_metadata`)
2. Listar todas as layers do frame recursivamente
3. Identificar assets por tipo:
   - **Imagens**: layers tipo IMAGE ou RECTANGLE com fill de imagem
   - **Ícones**: layers tipo VECTOR ou componentes de ícone
   - **Logos**: layers nomeadas com "logo" ou identificadas via Brand Guardian
   - **Ilustrações**: layers tipo GROUP com vetores complexos

### STEP 2 — Classificar no nível Atomic
Para cada asset identificado, classificar:

| Tipo de Asset | Nível Atomic | Pasta |
|---------------|-------------|-------|
| Ícone | Átomo | 01-Atomos/ |
| Logo | Átomo | 01-Atomos/ |
| Badge/Tag | Átomo | 01-Atomos/ |
| Imagem de card | Molécula | 02-Moleculas/ |
| Hero image | Organismo | 03-Organismos/ |
| Background de seção | Organismo | 03-Organismos/ |

### STEP 3 — Renomear assets
Aplicar naming convention Atomic:

```
Ícones:     atomo-icone-[nome]-v1.svg
Logos:      atomo-logo-[cliente]-[variante].svg
Badges:     atomo-badge-[tipo]-v1.svg
Imagens:    [nivel]-img-[descricao]-[cliente]-v1.png
Ilustrações: [nivel]-ilustracao-[descricao]-v1.svg
```

Exemplos:
- `atomo-icone-whatsapp-v1.svg`
- `atomo-logo-clinicabella-principal.svg`
- `molecula-img-card-procedimento-clinicabella-v1.png`
- `organismo-img-hero-clinicabella-v1.jpg`

### STEP 4 — Exportar e organizar
1. Exportar cada asset via Figma MCP (`export_assets`)
   - SVG para vetores (ícones, logos, ilustrações)
   - PNG @2x para imagens rasterizadas
   - WebP como alternativa otimizada
2. Organizar na estrutura de pastas:
   ```
   [cliente]-assets/
     └─ 01-Atomos/
     └─ 02-Moleculas/
     └─ 03-Organismos/
   ```

### STEP 5 — Gerar manifest
Criar `asset-manifest.json` com lista completa:

```json
{
  "cliente": "[nome]",
  "figma_source": "[url/id]",
  "data_extracao": "YYYY-MM-DD",
  "total_assets": N,
  "assets": [
    {
      "nome_original": "[nome no Figma]",
      "nome_renomeado": "[nome Atomic]",
      "nivel": "atomo|molecula|organismo",
      "formato": "svg|png|webp",
      "pasta": "[path relativo]"
    }
  ]
}
```

## Output esperado
```
Assets extraídos do Figma:
- Total: [N] assets coletados
- Átomos: [N] (ícones, logos, badges)
- Moléculas: [N] (imagens de cards, thumbnails)
- Organismos: [N] (hero images, backgrounds)
- Manifest: asset-manifest.json gerado
- Todos renomeados no padrão Atomic
```

## Regras invioláveis
- SEMPRE renomear — nunca usar nomes genéricos do Figma (ex: "Rectangle 42")
- SEMPRE classificar no nível Atomic correto
- SEMPRE exportar SVG para vetores, PNG @2x para raster
- SEMPRE gerar manifest para rastreabilidade
- NUNCA alterar o frame original no Figma
