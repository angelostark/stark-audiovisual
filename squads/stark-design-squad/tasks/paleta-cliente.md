# Task: Paleta do Cliente

## Metadata
- **Agent:** brand-guardian
- **Command:** `*paleta-cliente`
- **Args:** `{nome_do_cliente}`

## Descrição
Retorna a paleta de cores do cliente de forma rápida e direta, consultando o arquivo YAML de identidade visual.

## Pré-condições
- [ ] Nome do cliente informado

## Workflow

### STEP 1 — Localizar YAML do cliente
1. Buscar arquivo em `data/brands/[cliente].yaml`
2. Se não encontrar: tentar variações do nome (slug, lowercase, sem acentos)
3. Se não existir nenhum arquivo:
   - Informar que o cliente não tem guidelines cadastradas
   - Oferecer criar template YAML com `*consultar-marca`

### STEP 2 — Extrair paleta
Do YAML do cliente, extrair o bloco `brand_colors`:

```yaml
brand_colors:
  primary: "#hex"
  secondary: "#hex"
  accent: "#hex"
  background: "#hex"  # opcional
  text: "#hex"        # opcional
```

### STEP 3 — Exibir paleta formatada

```
🎨 Paleta — [Nome do Cliente]

| Cor | Hex | Uso |
|-----|-----|-----|
| Primary | #hex | Cor principal da marca |
| Secondary | #hex | Cor secundária |
| Accent | #hex | Destaque e CTAs |
| Background | #hex | Fundo padrão |
| Text | #hex | Cor de texto |
```

### STEP 4 — Alertas de completude
- Se `background` ou `text` estiverem vazios → avisar
- Se menos de 3 cores definidas → alertar guidelines incompletas

## Output esperado
Tabela com cores hex e uso de cada uma.

## Regras
- SEMPRE consultar o YAML — nunca inventar cores
- Se YAML não existe → informar e sugerir criação
- Formato rápido e direto — sem explicações longas
