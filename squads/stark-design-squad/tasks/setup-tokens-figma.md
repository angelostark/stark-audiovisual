# Task: Setup Design Tokens do Figma

## Metadata
- **Agent:** designer-figma
- **Command:** `*setup-tokens`
- **Args:** `{link_figma | nome_cliente} [--force]`

## Descricao
Extrai design tokens (cores, tipografia, espacamento, efeitos, grid) do arquivo Figma do cliente e organiza no projeto. Alimenta automaticamente o YAML do Brand Guardian com a identidade visual extraida, eliminando setup manual em demandas futuras.

## Pre-condicoes
- [ ] Link do Figma ou nome do cliente informado
- [ ] Figma MCP conectado

## Workflow

### STEP 1 — Acessar arquivo Figma do cliente
1. Abrir arquivo Figma pelo link ou buscar pelo nome do cliente
2. Listar todas as pages do arquivo
3. Identificar pages relevantes: "Assets", "Styles", "Brand", "Identidade", ou page principal com layouts recentes

### STEP 2 — Extrair cores (Color Tokens)
1. Ler todos os estilos de cor (Color Styles) do arquivo
2. Ler variaveis de cor (Color Variables) se existirem
3. Mapear cada cor encontrada para categoria:
   - `primary` — cor mais frequente / cor principal da marca
   - `secondary` — segunda cor mais usada
   - `accent` — cor de destaque (CTAs, botoes)
   - `background` — cor de fundo predominante
   - `text` — cor de texto principal
   - `text-light` — cor de texto secundario
   - `success`, `warning`, `error` — se houver
4. Registrar hex + nome original do Figma
5. Se nao houver Color Styles definidos:
   - Analisar os frames mais recentes
   - Extrair cores predominantes dos layouts
   - Alertar: "Cores extraidas de layouts — sem Color Styles formais"

### STEP 3 — Extrair tipografia (Typography Tokens)
1. Ler todos os Text Styles do arquivo
2. Mapear para categorias:
   - `heading` — fonte de titulos (maior peso/tamanho)
   - `body` — fonte de corpo de texto
   - `accent` — fonte decorativa/destaque (se houver)
   - `caption` — fonte pequena (se houver)
3. Para cada fonte registrar:
   - Font family
   - Font weight
   - Font size (mais comum)
   - Line height
   - Letter spacing
4. Se nao houver Text Styles definidos:
   - Analisar textos dos frames recentes
   - Extrair fontes predominantes
   - Alertar: "Tipografia extraida de layouts — sem Text Styles formais"

### STEP 4 — Extrair espacamento e grid (Spacing Tokens)
1. Ler Layout Grids aplicados nos frames principais
2. Identificar padroes de espacamento:
   - `padding` — espacamento interno (top, right, bottom, left)
   - `gap` — espacamento entre elementos
   - `margin` — margem externa padrao
3. Extrair grid settings:
   - Colunas, gutters, margins
   - Tipo: Grid, Columns, ou Rows
4. Se nao houver grids definidos: pular e alertar

### STEP 5 — Extrair efeitos (Effect Tokens)
1. Ler Effect Styles do arquivo (sombras, blurs, etc.)
2. Mapear:
   - `shadow-sm`, `shadow-md`, `shadow-lg` — sombras
   - `blur` — blur de fundo (se usado)
   - `overlay` — overlays (se usados)
3. Se nao houver Effect Styles: pular silenciosamente

### STEP 6 — Extrair assets de marca
1. Identificar logos na page "Assets" ou "Brand"
2. Para cada logo encontrado:
   - Nome da variante (principal, branco, icone, etc.)
   - Node ID no Figma
   - Uso recomendado (fundo claro, fundo escuro, etc.)
3. Identificar fotos recorrentes do cliente (se houver)

### STEP 7 — Organizar tokens no Figma
1. Verificar se existe page "Design Tokens" ou "Styles"
2. Se nao existir: criar page "🎨 Design Tokens"
3. Organizar tokens na page:
   - Section "Colors" — swatches com hex labels
   - Section "Typography" — amostras de cada estilo
   - Section "Spacing" — visual de grid e gaps
   - Section "Effects" — amostras de sombras/blurs
4. Se `--force` passado: sobrescrever tokens existentes
5. Se tokens ja existem e `--force` nao passado:
   - Comparar com existentes
   - Alertar diferencas
   - Perguntar se quer atualizar

### STEP 8 — Atualizar Brand Guardian YAML
1. Montar objeto com todos os tokens extraidos
2. Verificar se `data/brands/[cliente].yaml` existe
3. Se existe:
   - Fazer merge (tokens novos complementam, nao sobrescrevem manualmente editados)
   - Registrar `tokens_source: figma`
   - Registrar `tokens_updated_at: YYYY-MM-DD`
4. Se nao existe:
   - Criar novo YAML completo usando schema do Brand Guardian
   - Registrar `tokens_source: figma`
   - Registrar `tokens_created_at: YYYY-MM-DD`
5. Salvar YAML

### STEP 9 — Gerar relatorio
Exibir resumo:

```
🎨 Design Tokens — [Nome do Cliente]

📊 Tokens extraidos:
- Cores: [N] tokens ([lista: primary, secondary, accent...])
- Tipografia: [N] fontes ([heading, body...])
- Espacamento: [grid type] + [gap]px
- Efeitos: [N] estilos
- Logos: [N] variantes

📁 Fonte: [link do Figma]
📋 YAML: data/brands/[cliente].yaml [criado|atualizado]
📄 Page Figma: "🎨 Design Tokens" [criada|atualizada]

⚡ Proximo: qualquer demanda para [cliente] ja tem tokens prontos!
```

## Output esperado
- Tokens organizados no Figma (page dedicada)
- YAML do Brand Guardian criado/atualizado com tokens
- Relatorio visual no terminal

## Regras
- NUNCA inventar tokens — extrair SOMENTE do que existe no Figma
- Se nao encontrar estilos formais: extrair de layouts e ALERTAR
- SEMPRE registrar a fonte dos tokens (`figma` vs `manual`)
- SEMPRE preservar edicoes manuais no YAML (merge, nao sobrescrever)
- Se `--force` nao foi passado e tokens ja existem: PERGUNTAR antes de atualizar
- Tokens de cor devem ser hex (#RRGGBB) — converter rgba se necessario
- Minimo para considerar setup completo: cores (primary + secondary) + tipografia (heading + body)
