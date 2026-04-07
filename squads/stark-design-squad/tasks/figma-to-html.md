# Task: Figma to HTML

## Metadata
- **Agent:** web-designer-lp
- **Command:** `*figma-to-html`
- **Args:** `{figma_url|frame_id} {cliente} [--tailwind|--vanilla]`

## Descrição
Converte um design do Figma em HTML semântico e CSS responsivo, extraindo e renomeando assets, mapeando design tokens e gerando código pronto para produção.

## Pré-condições
- [ ] URL ou ID do frame Figma fornecido
- [ ] Nome do cliente informado
- [ ] Assets já extraídos (`*extrair-assets`) ou será executado automaticamente
- [ ] Brand Guardian consultado para design tokens do cliente

## Workflow

### STEP 1 — Analisar estrutura do Figma
1. Ler metadata completa do frame via Figma MCP
2. Mapear hierarquia de layers:
   - Identificar seções (hero, about, services, testimonials, CTA, footer)
   - Identificar componentes repetidos (cards, botões, inputs)
   - Identificar breakpoints (se existir frame mobile e desktop)
3. Capturar screenshot para referência visual

### STEP 2 — Extrair design tokens
Coletar do Figma e cruzar com Brand Guardian:

```css
:root {
  /* Cores — do Brand Guardian */
  --color-primary: #hex;
  --color-secondary: #hex;
  --color-accent: #hex;
  --color-bg: #hex;
  --color-text: #hex;

  /* Tipografia — do Brand Guardian */
  --font-heading: 'Font Name';
  --font-body: 'Font Name';

  /* Espaçamentos — do Figma */
  --spacing-xs: Npx;
  --spacing-sm: Npx;
  --spacing-md: Npx;
  --spacing-lg: Npx;
  --spacing-xl: Npx;

  /* Bordas */
  --radius-sm: Npx;
  --radius-md: Npx;
  --radius-lg: Npx;
}
```

### STEP 3 — Extrair e renomear assets
1. Se `*extrair-assets` ainda não foi executado: executar agora
2. Referenciar assets pelo nome Atomic no HTML
3. Gerar versões otimizadas (WebP + fallback PNG)

### STEP 4 — Mapear Figma → HTML semântico
Regras de conversão:

| Figma Element | HTML Element | Notas |
|---------------|-------------|-------|
| Frame (vertical auto-layout) | `<section>` ou `<div>` com flex-column | Section para seções principais |
| Frame (horizontal auto-layout) | `<div>` com flex-row | |
| Text (maior) | `<h1>` a `<h6>` | Hierarquia por tamanho/peso |
| Text (corpo) | `<p>` | |
| Text (label) | `<span>` ou `<label>` | |
| Retângulo + texto (botão) | `<button>` ou `<a class="btn">` | |
| Imagem | `<img>` com alt text | Obrigatório alt descritivo |
| Input field | `<input>` com `<label>` | Acessibilidade |
| Grupo repetido | `<ul>/<li>` ou grid | Cards, features, etc. |
| Ícone | `<svg>` inline ou `<img>` | SVG inline preferido |

### STEP 5 — Gerar HTML
Estrutura base:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Cliente] — [Título da LP]</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header><!-- Organismo: header --></header>
  <main>
    <section class="hero"><!-- Organismo: hero --></section>
    <section class="services"><!-- Organismo: serviços --></section>
    <section class="testimonials"><!-- Organismo: depoimentos --></section>
    <section class="cta"><!-- Organismo: CTA --></section>
  </main>
  <footer><!-- Organismo: footer --></footer>
</body>
</html>
```

### STEP 6 — Gerar CSS
Se `--tailwind`: gerar com classes Tailwind + config personalizado
Se `--vanilla` (padrão): gerar CSS vanilla com custom properties

Requisitos CSS:
- Mobile-first (375px base)
- Breakpoints: 768px (tablet), 1024px (laptop), 1280px+ (desktop)
- Usar CSS Grid ou Flexbox conforme auto-layout do Figma
- Custom properties para todos os design tokens
- Sem `!important` (código limpo)

### STEP 7 — Verificar qualidade
1. **Semântica HTML**: headings em ordem (h1→h2→h3), landmarks (header, main, footer, nav)
2. **Acessibilidade WCAG**:
   - Alt text em todas as imagens
   - Contraste mínimo AA (4.5:1)
   - Focus states em elementos interativos
   - Labels em todos os inputs
3. **Responsividade**: verificar em 375px, 768px, 1280px
4. **Performance**: imagens otimizadas, CSS minificável

### STEP 8 — Organizar output
```
[cliente]-lp/
  ├── index.html
  ├── styles.css (ou tailwind.config.js + input.css)
  ├── assets/
  │   ├── 01-Atomos/
  │   ├── 02-Moleculas/
  │   └── 03-Organismos/
  ├── fonts/ (se fontes locais)
  └── asset-manifest.json
```

## Output esperado
```
LP convertida de Figma para HTML:
- Cliente: [nome]
- Seções: [N] organismos convertidos
- Assets: [N] extraídos e renomeados
- CSS: [tailwind|vanilla] com design tokens
- Responsivo: mobile (375px) + tablet (768px) + desktop (1280px)
- WCAG: verificado (AA)
- Pasta: [cliente]-lp/
```

## Regras invioláveis
- SEMPRE HTML semântico — nunca `<div>` genérico onde cabe `<section>`, `<nav>`, `<article>`
- SEMPRE mobile-first no CSS
- SEMPRE alt text descritivo em imagens (não "imagem" ou "foto")
- SEMPRE design tokens via CSS custom properties
- SEMPRE renomear assets no padrão Atomic antes de referenciar
- NUNCA usar IDs para estilização — apenas classes
- NUNCA inline styles — tudo no CSS
- NUNCA ignorar acessibilidade — WCAG AA mínimo
