---
name: analisar-artes
description: >
  Analisa artes do time de design contra as 16 regras do Design System Stark.
  Baixa imagens do Google Drive, avalia visualmente cada arte, gera scorecard
  por arte e resumo por designer, e grava resultados no Google Sheets.

  Use SEMPRE que o usuario pedir: "analisar artes", "revisar artes",
  "checar artes do cliente", "avaliar design", "quality check de artes",
  "analise de artes", "verificar artes", "scorecard de artes",
  ou qualquer variacao de analisar/revisar/avaliar artes do time de design.
---

# Analisar Artes — Design System Review

Essa skill automatiza a revisao de artes do time de design contra as 16 regras de qualidade do Design System Stark.

1. Coleta imagens do Google Drive (via script Python)
2. Avalia visualmente cada arte contra as 16 regras
3. Gera scorecard por arte + resumo por designer
4. Grava resultados no Google Sheets (com confirmacao)

---

## Pre-requisitos

- `automacoes/credentials.json` configurado (service account Google)
- Pasta "Clientes" do Drive compartilhada com o email do service account
- Dependencias: `pip install google-api-python-client google-auth`
- Planilha "Analise de Artes - AV" criada e compartilhada com service account (para gravacao)

Se faltar algo, oriente o usuario a seguir `automacoes/SETUP-GOOGLE-API.md`.

---

## Passo a passo de execucao

### ETAPA 1 — Coletar parametros

Pergunte ao usuario:

1. **Cliente:** Qual cliente? (ou "all" para todos)
2. **Periodo:** today, week, month, ou data especifica?
3. **Limite:** Quantas artes no maximo? (default: 50)

Se o usuario ja forneceu o cliente e/ou periodo no pedido original, use esses valores sem perguntar.

### ETAPA 2 — Executar script Python

Rode o script para baixar as imagens:

```bash
python3 /Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/analisar_artes.py \
  --client "[CLIENTE]" \
  --period "[PERIODO]" \
  --max-files [LIMITE]
```

Se o usuario especificou uma data exata:
```bash
python3 /Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/analisar_artes.py \
  --client "[CLIENTE]" \
  --date "[YYYY-MM-DD]"
```

Capture o JSON de output do script. Ele contem a lista de imagens com `local_path`, `designer`, `drive_link`, etc.

**Se o script falhar:** mostre o erro e tente resolver (credenciais, pasta nao encontrada, etc.).

**Se nenhuma imagem for encontrada:** informe ao usuario e pergunte se quer tentar outro periodo ou cliente.

### ETAPA 3 — Analisar cada imagem

Para cada imagem no JSON retornado pelo script:

1. Use a ferramenta **Read** no `local_path` para visualizar a imagem
2. Avalie contra as **16 regras** abaixo
3. Atribua um veredicto para cada regra: **OK**, **ALERTA**, **VIOLACAO**, ou **N/A**

#### Rubrica de avaliacao (16 regras)

**CAPA DEVE TER:**

| # | Regra | Avaliabilidade | O que verificar |
|---|-------|---------------|-----------------|
| 1 | Logo/Twitter-X | ALTA | Presenca do logo da clinica ou icone do Twitter/X |
| 2 | Titulo + Subtitulo | ALTA | Texto principal e texto secundario visiveis |
| 3 | CTA (Call to Action) | ALTA | Botao ou texto de acao (ex: "Saiba mais", "Agende") |
| 4 | Imagem de apoio/ilustracao | ALTA | Elemento visual de suporte ao conteudo |
| 5 | Foto do medico | MEDIA | Foto do profissional (N/A se nao aplicavel ao tipo de post) |
| 6 | Antes/depois coberto | MEDIA | Resultado visual coberto quando aplicavel (N/A se nao for post de resultado) |

**CAPA NAO DEVE TER:**

| # | Regra | Avaliabilidade | O que verificar |
|---|-------|---------------|-----------------|
| 7 | Texto-only com cor solida | ALTA | Fundo de cor solida com apenas texto, sem elementos visuais |
| 8 | Ilustracao escondida | MEDIA | Ilustracao muito pequena ou coberta por outros elementos |
| 9 | Fotos stock image | BAIXA | Fotos genericas de banco de imagem (subjetiva) |
| 10 | Info fora do grid 1080x1080 | MEDIA | Conteudo cortado ou fora da area segura |
| 11 | Baixa criatividade/repeticao | BAIXA | Design muito similar a outros recentes (N/A sem historico) |
| 12 | Quadrados com resultados | MEDIA | Layout de grid quadrado mostrando resultados (evitar) |
| 13 | Gradientes excessivos | MEDIA | Uso exagerado de gradientes que prejudica legibilidade |

**CARROSSEL (quando aplicavel — marcar N/A se for post unico):**

| # | Regra | Avaliabilidade | O que verificar |
|---|-------|---------------|-----------------|
| 14 | Max 1 card sem ilustracao | ALTA | No maximo 1 slide do carrossel pode nao ter ilustracao |
| 15 | Ultimo card com CTA + foto + logo | ALTA | Ultimo slide deve ter call to action, foto do medico e logo |
| 16 | Nao repetir estilo >1 mes | BAIXA | Estilo visual nao deve se repetir por mais de 1 mes (N/A sem historico) |

#### Regras de avaliacao

- **OK**: A regra e atendida
- **ALERTA**: Atende parcialmente ou tem margem para melhoria
- **VIOLACAO**: Regra claramente nao atendida
- **N/A**: Regra nao aplicavel (ex: regras 14-16 para post unico, regra 5 para post sem medico, regras 11 e 16 sem historico)

Para regras de "NAO deve ter" (7-13): **OK** = nao tem o problema, **VIOLACAO** = tem o problema.

#### Pontuacao

```
Score = (OK * 1.0 + ALERTA * 0.5) / total_regras_aplicaveis * 100
```

| Score | Classificacao |
|-------|---------------|
| 90-100% | Excelente |
| 70-89% | Bom |
| 50-69% | Precisa melhorar |
| <50% | Critico |

### ETAPA 4 — Gerar relatorio no chat

Apresente o relatorio em duas partes:

#### Parte A: Scorecard por arte

Para cada arte analisada:

```
## [nome_arquivo] — [Score]% ([Classificacao])
Designer: [nome]
Link: [drive_link]

| # | Regra | Veredicto | Nota |
|---|-------|-----------|------|
| 1 | Logo/Twitter-X | OK | — |
| 2 | Titulo + Subtitulo | ALERTA | Subtitulo pouco legivel |
| ... | ... | ... | ... |
```

Inclua notas apenas para ALERTA e VIOLACAO, explicando brevemente o problema.

#### Parte B: Resumo por designer

```
## Resumo por Designer

| Designer | Artes | Score Medio | Classificacao | Top Violacao |
|----------|-------|-------------|---------------|-------------- |
| Humberto | 5 | 87% | Bom | CTA ausente (2x) |
| Joao | 3 | 92% | Excelente | — |
```

Se algum designer apareceu como "Desconhecido", pergunte ao usuario quem fez a arte.

### ETAPA 5 — Gravar no Google Sheets (com confirmacao)

**Antes de gravar, pergunte ao usuario:**
> "Quer que eu grave esses resultados na planilha 'Analise de Artes - AV'?"

Se confirmado, use o script Python ou gspread para gravar:

#### Aba "Avaliacoes"

Colunas (nesta ordem):
`data_analise | cliente | designer | arquivo | tipo | drive_link | r1_logo | r2_titulo | r3_cta | r4_imagem | r5_foto_medico | r6_antes_depois | r7_texto_only | r8_ilustracao_oculta | r9_stock_image | r10_grid | r11_criatividade | r12_quadrados | r13_gradientes | r14_carrossel_max1 | r15_carrossel_ultimo | r16_carrossel_estilo | score_pct | classificacao | notas`

Valores por regra: OK | ALERTA | VIOLACAO | N/A

#### Aba "Resumo Semanal"

Colunas:
`semana | designer | total_artes | score_medio | classificacao | violacoes | alertas | top_violacao_1 | top_violacao_2`

**Sheet ID:** `1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I` (tambem em `automacoes/analisar_artes.py` como `ANALISE_SHEET_ID`)

Para gravar, execute um script Python inline via Bash que use gspread, seguindo o padrao de `preencher_entregas_clickup.py`:
```python
import gspread
from google.oauth2.service_account import Credentials
creds = Credentials.from_service_account_file(
    '/Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets'])
client = gspread.authorize(creds)
ss = client.open_by_key('1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I')
aba = ss.worksheet('Avaliacoes')
aba.append_row([...dados...])
```

---

## Edge cases

| Caso | Tratamento |
|------|-----------|
| Videos na pasta | Filtrados pelo script, listados em `skipped_files` — informar o usuario |
| Pasta vazia | Reportar, perguntar outro periodo |
| Cliente nao encontrado | Erro + sugerir `--client all` para listar clientes |
| Designer desconhecido | Perguntar ao usuario quem fez a arte |
| Imagem >20MB | Pulada pelo script, reportada |
| Nenhuma arte no periodo | Sugerir outro periodo |
| Carrossel vs estatico | Se pasta tiver multiplas imagens com nomes sequenciais, tratar como carrossel |
| Planilha nao configurada | Pular etapa 5, informar como configurar |

---

## Dependencias

| Componente | Tipo | Caminho |
|------------|------|---------|
| Script de coleta | Python | `automacoes/analisar_artes.py` |
| Script de upload (reutilizado) | Python | `automacoes/upload_drive.py` |
| Credenciais Google | JSON | `automacoes/credentials.json` |
| Setup guide | Docs | `automacoes/SETUP-GOOGLE-API.md` |

### Instalar dependencias Python
```bash
pip install google-api-python-client google-auth gspread
```
