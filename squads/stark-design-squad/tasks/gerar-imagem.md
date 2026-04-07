# Task: Gerar Imagem via Nanobanana

## Metadata
- **Agent:** designer-figma
- **Command:** `*gerar-imagem`
- **Args:** `{prompt} [--editar imagem_ref] [--cliente nome]`

## Descrição
Gera ou edita imagens usando Nanobanana (Google Gemini 2.5 Flash Image Generation) para uso em layouts do Design Squad.

## Pré-condições
- [ ] Briefing verificado no ClickUp
- [ ] Brand Guardian consultado para paleta e tom visual do cliente
- [ ] Confirmado que não há fotos profissionais disponíveis para o caso de uso

## Workflow

### STEP 1 — Validar necessidade
1. Verificar se o cliente tem fotos profissionais no Drive para o briefing
2. Se sim → usar fotos reais, NÃO gerar via IA
3. Se não → prosseguir com geração

### STEP 2 — Preparar prompt
1. Consultar Brand Guardian para paleta de cores e tom visual
2. Montar prompt descritivo incluindo:
   - Estilo visual desejado (clean, bold, minimal, etc.)
   - Paleta de cores do cliente (hex codes)
   - Elementos obrigatórios do briefing
   - Formato e resolução (1080x1350, 1080x1920, etc.)
3. Se `--editar` fornecido: incluir referência da imagem base

### STEP 3 — Gerar imagem
1. Enviar prompt para Nanobanana MCP
2. Se modo edição (`--editar`):
   - Carregar imagem de referência
   - Aplicar edição solicitada (remover fundo, ajustar cor, trocar elementos)
3. Se modo geração:
   - Gerar imagem nova a partir do prompt
4. Se precisa de variações:
   - Gerar 2-3 alternativas para seleção

### STEP 4 — Validar resultado
1. Verificar coerência com paleta do Brand Guardian
2. Verificar que NÃO contém:
   - Pessoas reais identificáveis
   - Simulação de resultados de procedimentos médicos
   - Texto ilegível ou com erros
3. Se aprovado → prosseguir
4. Se não → ajustar prompt e regenerar (max 3 tentativas)

### STEP 5 — Registrar e exportar
1. Salvar imagem no Figma dentro do frame do cliente
2. Registrar metadata:
   - `gerado_por: nanobanana`
   - `prompt_usado: "{prompt completo}"`
   - `data_geracao: YYYY-MM-DD`
   - `cliente: {nome}`
3. Nomear: `[cliente]-ia-[descricao]-[AAAAMMDD]-v[numero]`
4. Informar que a imagem é gerada por IA (obrigatório para o laudo QA)

## Output esperado
```
Imagem gerada via Nanobanana:
- Nome: [nome do arquivo]
- Resolução: [WxH]
- Prompt: "[prompt resumido]"
- Flag: 🤖 Gerada por IA
- Status: Pronta para uso no layout
```

## Regras invioláveis
- SEMPRE informar no laudo QA que a imagem foi gerada por IA
- NUNCA gerar imagens de pessoas reais identificáveis
- NUNCA simular resultados de procedimentos médicos (antes/depois)
- SEMPRE salvar o prompt para reprodutibilidade
- SEMPRE validar coerência com paleta do Brand Guardian
- Preferir fotos reais quando disponíveis — IA é complemento, não substituto
