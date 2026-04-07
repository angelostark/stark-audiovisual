---
task: Indexar Layout
responsavel: "@designer-figma"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Cliente (obrigatorio)
  - Figma URL ou Node ID (obrigatorio)
  - Tipo: estatico, carrossel, capa, stories, lp
  - Drive Path (link ou path no Drive)
  - Nota QA e veredito (do *avaliar)
  - Refacoes (do Monitor Refacoes)
Saida: |
  - Linha inserida na aba do cliente na planilha Layout Index
  - Cache local salvo em data/layouts/{cliente}/{id}.json
  - Confirmacao com ID gerado
Checklist:
  - "[ ] Coletar dados do layout (Figma, Drive, QA, refacoes)"
  - "[ ] Gerar ID unico no padrao Stark"
  - "[ ] Classificar tipo e subtipo"
  - "[ ] Extrair tags automaticamente"
  - "[ ] Criar aba do cliente se nao existir"
  - "[ ] Inserir linha na planilha Layout Index"
  - "[ ] Salvar cache local em data/layouts/"
  - "[ ] Confirmar indexacao ao usuario"
---

# *indexar-layout

Registra um layout entregue no indice (Google Sheets) para consulta futura. Executado automaticamente apos exportar entrega ou manualmente.

## Uso

```
*indexar-layout --cliente "Dr George" --figma-url "https://figma.com/..." --tipo estatico
*indexar-layout --cliente "Dra Camila" --figma-node "123:456" --drive-path "link_drive"
```

## Planilha

- **ID**: `1kZOi4zw8ih8bI7mJsiQXYyMKFvCPotBkzWnpIP3B1Sg`
- **Estrutura**: uma aba por cliente
- **Colunas (18)**: ID, Tipo, Subtipo, Data Criacao, Designer, Figma URL, Figma Node ID, Drive Path, Formato, Nota QA, Veredito QA, Refacoes, Tempo (dias), Feedback Externo, Fonte Feedback, Tags, Engajamento, Observacoes

## Fluxo

1. Receber dados do layout (cliente + figma obrigatorios)
2. Gerar ID unico:
   - Padrao: `{cliente_slug}-{tipo}-{AAAAMMDD}-v{numero}`
   - Ex: `drgeorge-estatico-20260331-v1`
   - Se ja existe ID com mesma data/tipo: incrementar versao (v2, v3...)
3. Classificar tipo automaticamente se nao informado:
   - Carrossel: multiplos frames sequenciais
   - Estatico: frame unico feed (1080x1350)
   - Capa: frame unico reels (1080x1920)
   - Stories: frame unico stories (1080x1920)
   - LP: landing page
4. Classificar subtipo automaticamente por tags/conteudo:
   - antes_depois, informativo, promocional, institucional, depoimento
5. Extrair tags automaticamente:
   - Do nome do frame Figma
   - Do tipo de conteudo
   - Da paleta de cores predominante
6. Coletar dados complementares:
   - Nota QA e veredito: do ultimo *avaliar (se disponivel)
   - Refacoes: do Monitor Refacoes (se disponivel)
   - Tempo: calcular dias entre briefing e aprovacao (se datas disponiveis)
   - Designer: do responsavel da task no ClickUp
   - Formato: dimensoes do frame Figma
7. Acessar planilha Layout Index via Google Sheets API
8. Verificar se aba do cliente existe:
   - Se nao: criar aba com headers (18 colunas)
   - Se sim: localizar proxima linha vazia
9. Inserir linha com todos os dados
10. Salvar cache local: `data/layouts/{cliente_slug}/{id}.json`
11. Confirmar ao usuario: "Layout indexado: {id} na aba {cliente}"

## Geracao de ID

```
{cliente_slug} = nome do cliente em lowercase, sem acentos, sem espacos
  Ex: "Dr George" → "drgeorge"
  Ex: "Dra. Camila" → "dracamila"
  Ex: "Clinica Bella" → "clinicabella"

{tipo} = estatico | carrossel | capa | stories | lp

{AAAAMMDD} = data de criacao

v{numero} = versao (incrementa se mesmo cliente+tipo+data ja existe)
```

## Headers da Planilha (criar na primeira indexacao)

```
ID | Tipo | Subtipo | Data Criacao | Designer | Figma URL | Figma Node ID | Drive Path | Formato | Nota QA | Veredito QA | Refacoes | Tempo (dias) | Feedback Externo | Fonte Feedback | Tags | Engajamento | Observacoes
```

## Regras

- Cliente e Figma URL/Node ID sao obrigatorios
- Se tipo nao informado: tentar classificar automaticamente
- Se nao conseguir classificar: perguntar ao usuario
- Nunca duplicar: verificar se ID ja existe antes de inserir
- Cache local e complementar — planilha e a fonte de verdade
- Tags sao geradas automaticamente mas podem ser editadas depois
- Campos vazios sao aceitos (feedback, engajamento vem depois)
