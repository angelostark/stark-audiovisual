---
name: figma-export-para-drive
description: >
  Exporta frames do Figma como PNG, faz upload automatico para a pasta do
  cliente no Google Drive (criando subpasta com a data do nome do frame),
  busca a SUBTAREFA correspondente no ClickUp pelo nome do frame, adiciona
  um comentário com o LINK DA PASTA no Drive e notifica (@menciona) o
  responsável da TAREFA MÃE.

  Use SEMPRE que o usuário pedir: "exportar do Figma para o Drive",
  "jogar [arquivo] no Drive", "exportar design para o cliente",
  "enviar Figma para Drive", "fazer upload do Figma", "mandar [nome] pro Drive",
  "exportar [nome] e comentar no ClickUp", "jogar no drive e comentar",
  ou qualquer variação de mover, exportar ou enviar frames do Figma para o
  Google Drive e notificar via ClickUp.
---

# Figma → Drive → ClickUp

Essa skill automatiza o fluxo completo de entrega de design:
1. Exporta o frame do Figma como PNG
2. Faz upload automatico para a pasta correta no Google Drive (via script)
3. Busca a **subtarefa** no ClickUp, posta o link da **pasta** do Drive como comentário e notifica o responsável da **tarefa mãe**

---

## Pre-requisitos

- `automacoes/credentials.json` configurado (service account Google)
- Pasta "Clientes" do Drive compartilhada com o email do service account
- Dependencias: `pip install google-api-python-client google-auth`

Se faltar algo, oriente o usuario a seguir `automacoes/SETUP-GOOGLE-API.md` e compartilhar a pasta "Clientes" do Drive com o service account.

---

## Convenção de nomenclatura dos frames

Os frames no Figma seguem este padrão:
```
[DATA] - [NOME DO DRIVE]
```
Exemplos:
- `2026-03-17 - Stark`
- `2026-03-20 - Nike Brasil`
- `2026-03-15 - Clínica Saúde`

A **data** (antes do ` - `) define a subpasta no Drive.
O **nome do Drive** (depois do ` - `) é o nome exato da pasta do cliente no Google Drive.

---

## O que o usuário precisa fornecer

- **Link do Figma** (URL do arquivo/frame) ou o nome do frame
- Opcionalmente: qual frame específico exportar (se não informar, pergunte)

---

## Passo a passo de execução

### ETAPA 1 — Localizar o frame no Figma

Se o usuário forneceu um link (ex.: `https://figma.com/design/XYZABC/Nome?node-id=1-2`):
- Extraia o `fileKey` da URL (segmento após `/design/`)
- Extraia o `nodeId` do parâmetro `node-id` convertendo `-` para `:` (ex.: `1-2` → `1:2`)

Use `mcp__claude_ai_Figma__get_metadata` com `fileKey` e `nodeId` para confirmar o nome do frame e listar frames filhos.

Se não tiver URL, peça ao usuário que copie o link via "Copy link to selection" no Figma.

### ETAPA 2 — Extrair data e nome do Drive a partir do nome do frame

Parse o nome do frame no padrão `[DATA] - [NOME DO DRIVE]`:
- **data** = tudo antes do primeiro ` - ` (formato `YYYY-MM-DD`)
- **nome_drive** = tudo depois do primeiro ` - ` (texto exato)

Exemplos:
```
"2026-03-17 - Stark"       → data: "2026-03-17", nome_drive: "Stark"
"2026-03-20 - Nike Brasil"  → data: "2026-03-20", nome_drive: "Nike Brasil"
```

Se o nome do frame não tiver o padrão `[DATA] - [NOME]`, pergunte ao usuário antes de prosseguir.

### ETAPA 3 — Identificar tipo de post e exportar

Use `mcp__claude_ai_Figma__get_metadata` no frame principal para verificar frames filhos.

#### Estático (sem frames filhos)
Exporte somente o frame principal com `mcp__claude_ai_Figma__get_screenshot`:
```
/tmp/figma_exports/[data]-[nome_drive].png
```

#### Carrossel (com frames filhos = cards)
Cada filho é um card/slide. Exporte cada um com `mcp__claude_ai_Figma__get_screenshot` usando o `nodeId` de cada filho:
```
/tmp/figma_exports/[data]-[nome_drive]-card-01.png
/tmp/figma_exports/[data]-[nome_drive]-card-02.png
/tmp/figma_exports/[data]-[nome_drive]-card-03.png
```
Numere com zero à esquerda (01, 02, 03...) preservando a ordem dos frames filhos.

Antes de exportar, crie o diretório:
```bash
mkdir -p /tmp/figma_exports
```

Salve cada screenshot no diretório usando o Write tool ou Bash com curl/base64 conforme o retorno do MCP.

### ETAPA 4 — Upload automatico para o Google Drive

O script `automacoes/upload_drive.py` navega automaticamente a hierarquia de pastas:

```
Clientes / [nome_drive] / Cronograma de Conteúdo / Artes / [ano] / [mês] / [data]
```

E faz upload de todos os PNGs. Se a pasta da data não existir, cria automaticamente.

#### 4a. Executar o upload

```bash
python3 automacoes/upload_drive.py \
  --client "[NOME_DRIVE]" \
  --date "[DATA]" \
  --files /tmp/figma_exports/*.png
```

Exemplos:
```bash
# Post estatico
python3 automacoes/upload_drive.py \
  --client "Stark" \
  --date "2026-03-17" \
  --files /tmp/figma_exports/2026-03-17-Stark.png

# Carrossel
python3 automacoes/upload_drive.py \
  --client "Nike Brasil" \
  --date "2026-03-20" \
  --files /tmp/figma_exports/2026-03-20-Nike\ Brasil-card-01.png \
          /tmp/figma_exports/2026-03-20-Nike\ Brasil-card-02.png \
          /tmp/figma_exports/2026-03-20-Nike\ Brasil-card-03.png
```

#### 4b. Capturar o resultado

O script retorna JSON no stdout. Capture o `folder_link` do output:
```json
{
  "folder_id": "abc123",
  "folder_link": "https://drive.google.com/drive/folders/abc123",
  "created": true,
  "files": [
    {"name": "card-01.png", "id": "...", "link": "..."}
  ]
}
```

Guarde o `folder_link` para usar no comentário do ClickUp.

#### 4c. Dry run (para testar sem upload)

```bash
python3 automacoes/upload_drive.py \
  --client "Stark" \
  --date "2026-03-17" \
  --dry-run
```

#### 4d. FALLBACK — Se o script falhar

Se o upload falhar (credenciais ausentes, pasta não compartilhada, etc.):

1. Mostre o erro do script ao usuario
2. Informe o caminho completo onde os arquivos devem ir no Drive:
```
📁 Caminho no Drive:
Clientes / [nome_drive] / Cronograma de Conteúdo / Artes / [ano] / [mês] / [data]
```
3. Liste os PNGs locais em `/tmp/figma_exports/`
4. Pergunte:
> "O upload automatico falhou. Suba os PNGs manualmente na pasta acima e me mande o **link da pasta** no Drive pra continuar com o ClickUp."
5. Aguarde o `folder_link` do usuario antes de prosseguir.

### ETAPA 5 — Encontrar a subtarefa no ClickUp

Use `mcp__claude_ai_ClickUp__clickup_search` com o `nome_drive` como termo de busca:
```
query: "[NOME_DRIVE]"
```
Ex.: frame `2026-03-17 - Stark` → buscar `"Stark"` no ClickUp.

**Regras de desambiguação:**
- Se encontrar múltiplas tarefas, priorize as com status ativo (não concluído)
- Se ainda houver ambiguidade, mostre as opções ao usuário e peça confirmação
- Se a tarefa encontrada não tiver `parent`, pode ser a tarefa mãe — confirme com o usuário

### ETAPA 6 — Encontrar o responsável da tarefa mãe

Com o ID da subtarefa:
1. Use `mcp__claude_ai_ClickUp__clickup_get_task` para obter detalhes e o campo `parent`
2. Use `mcp__claude_ai_ClickUp__clickup_get_task` novamente com o `parent` ID para obter a tarefa mãe
3. Leia o campo `assignees` da tarefa mãe — pegue todos os assignees

Guarde o `id` e o `username` de cada assignee para a menção.

### ETAPA 7 — Postar comentário na subtarefa

Use `mcp__claude_ai_ClickUp__clickup_create_task_comment` na subtarefa com este formato:

```
📁 Arquivos exportados para o Google Drive:
• Pasta de entregas [DATA]: [FOLDER_LINK]

CC: @[Nome do Responsável 1] @[Nome do Responsável 2]
```

Para mencionar usuários no ClickUp, use o ID do assignee no formato de menção do ClickUp.

Use `assignee` com o ID do responsável da tarefa mãe e `notify_all: true` para garantir a notificação.

### ETAPA 7.1 — Atualizar status da subtarefa para "edição concluída"

Imediatamente após postar o comentário, atualize o status da subtarefa:

Use `mcp__claude_ai_ClickUp__clickup_update_task` na subtarefa:
```
task_id: [ID DA SUBTAREFA]
status: "edição concluída"
```

Isso move a tarefa automaticamente de "a ser feito" ou "edição" para "edição concluída", sinalizando que os arquivos foram entregues.

> **Nota:** Se o status "edição concluída" não existir na lista, tente variações como "Edição Concluída", "edição concluida", ou pergunte ao usuário qual é o status correto.

### ETAPA 8 — Resumo final

Ao concluir, apresente:

```
✅ Exportação concluída!

🎨 Frame: [DATA] - [NOME DO DRIVE]
📦 Tipo: [Estático / Carrossel com N cards]

📁 Drive:
   └── Pasta: [NOME DO DRIVE] / [ANO] / [MÊS] / [DATA]
   └── Link: [folder_link]
   └── Arquivos: [lista dos PNGs]

🔗 ClickUp:
   └── Subtarefa: "[Nome da Subtarefa]"
   └── Status: edição concluída ✅
   └── Comentário postado com link do Drive
   └── Responsável notificado: @[Nome(s)] (tarefa mãe: "[nome da tarefa mãe]")
```

Se alguma etapa falhou, informe claramente o que não foi possível e por quê.

---

## Erros comuns e como lidar

| Situacao | Acao |
|----------|------|
| Nome do frame nao segue padrao `[DATA] - [NOME]` | Perguntar data e nome do cliente antes de prosseguir |
| Arquivo Figma nao encontrado | Pedir o link direto do Figma |
| `credentials.json` nao encontrado | Orientar: `automacoes/SETUP-GOOGLE-API.md` |
| Pasta "Clientes" nao acessivel no Drive | Pedir que compartilhe com o service account |
| Pasta do cliente nao existe no Drive | Mostrar erro e pedir que crie no Drive |
| Upload falhou | Usar fallback manual (Etapa 4d) |
| Subtarefa ClickUp nao encontrada | Mostrar tarefas similares e pedir confirmacao |
| Tarefa encontrada nao tem tarefa mae (`parent` vazio) | Confirmar com o usuario se e a tarefa correta |
| Multiplos assignees na tarefa mae | Mencionar todos no comentario |
| Screenshot do Figma retorna erro | Verificar nodeId, tentar com frame pai |

---

## Dependencias

| Componente | Tipo | Caminho |
|------------|------|---------|
| Script de upload | Python | `automacoes/upload_drive.py` |
| Credenciais Google | JSON | `automacoes/credentials.json` |
| Setup guide | Docs | `automacoes/SETUP-GOOGLE-API.md` |

### Instalar dependencias Python
```bash
pip install google-api-python-client google-auth
```

---

## Status de integracao

| Servico | Status | Via |
|---------|--------|-----|
| Figma | ✅ Automatico | MCP (`get_metadata`, `get_screenshot`) |
| Google Drive | ✅ Automatico | Script `upload_drive.py` + Service Account |
| ClickUp | ✅ Automatico | MCP (`search`, `get_task`, `create_task_comment`) |
