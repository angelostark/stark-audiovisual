---
name: preencher-entrega-posts
description: >
  Calcula a % de entrega de posts no prazo (até quarta 20h) para cada
  designer/editor do time Audiovisual da Stark. Busca do ClickUp via MCP,
  salva dados brutos no Google Sheets, e atualiza planilha de entregas.

  Use SEMPRE que o usuário pedir: "preencher entrega de posts", "verificar entregas",
  "calcular entregas da semana", "meta de entrega", "prazo de entrega posts",
  "rodar entrega posts", ou qualquer variação de verificar/calcular/preencher
  entregas de posts do time audiovisual.
---

# Preencher Entrega de Posts — Stark Audiovisual

Essa skill busca tarefas do ClickUp via MCP, salva dados brutos no Google Sheets,
calcula o percentual de entregas no prazo (quarta 20h) por designer/editor,
e atualiza a planilha de entregas.

> **REGRA CRÍTICA:** Salve TODOS os resultados de busca em arquivos JSON imediatamente
> após cada chamada. NÃO dependa do contexto inline — ele será perdido no compaction.
> Processe os dados via script Python, nunca inline.

---

## Arquitetura

```
Skill → ClickUp MCP (7 buscas) → /tmp/*.json → Python → Google Sheets (Dados Brutos + Entregas)
```

---

## Constantes

### Planilha (tudo na mesma)
```
SHEET_ID = "1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA"
```
- Aba "Dados Brutos" → dados crus das tarefas (limpa e reescreve a cada execução)
- Aba "Status" → timestamp e status da última execução
- Aba do mês (Janeiro, Fevereiro, Março...) → resultado de entregas por pessoa

### Listas ClickUp (IDs fixos)
```
LISTAS = [
  "901305832980",   # Posts do Insta 2.0
  "900702180610",   # Edição de Vídeos 2.1
  "901324888130"    # Agenda de Postagem 3.0
]
```

### Time Audiovisual (ClickUp UID → Nome)
```
TEAM = {
  82154730:  "Humberto",
  112104835: "João",
  84856123:  "Eloy",
  112104837: "Max",
  106090854: "Karyne",
  106172497: "Milena",
  188585120: "Ebertty",
  82029622:  "André",
  248549658: "Mateus Redman"
}
```

### Status considerados "entregue"
```
STATUS_ENTREGUE = [
  "done", "closed", "edição concluída", "aguardando postagem",
  "concluído", "concluída", "encerramento da tarefa", "aprovado",
  "arte aprovada", "finalizado"
]
```

### Meta
```
META_PERCENTUAL = 97%
```

---

## Passo a passo de execução

### ETAPA 1 — Calcular datas da semana e salvar em arquivo

Use Bash para calcular as datas no fuso **America/Bahia (UTC-3)** e salvar tudo em `/tmp/entrega_config.json`:

```bash
export TZ="America/Bahia"

# Segunda-feira da semana atual
WEEKDAY=$(date +%u)
OFFSET=$(( WEEKDAY - 1 ))
SEGUNDA=$(date -v-${OFFSET}d +%Y-%m-%d)
DOMINGO=$(date -v-${OFFSET}d -v+6d +%Y-%m-%d)

# Prazo: quarta-feira às 20:00
QUARTA=$(date -v-${OFFSET}d -v+2d +%Y-%m-%d)
PRAZO="${QUARTA}T20:00:00"
PRAZO_MS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${PRAZO}" +%s)000

# Dias da semana no formato DD/MM
DIAS=()
for i in 0 1 2 3 4 5 6; do
  DIAS+=($(date -v-${OFFSET}d -v+${i}d +%d/%m))
done

SEMANA_STR="$(date -v-${OFFSET}d +%d/%m) a $(date -v-${OFFSET}d -v+6d +%d/%m/%Y)"

# Salvar config em arquivo JSON
cat > /tmp/entrega_config.json << EOF
{
  "segunda": "$SEGUNDA",
  "domingo": "$DOMINGO",
  "prazo": "$PRAZO",
  "prazo_ms": ${PRAZO_MS},
  "dias": ["${DIAS[0]}", "${DIAS[1]}", "${DIAS[2]}", "${DIAS[3]}", "${DIAS[4]}", "${DIAS[5]}", "${DIAS[6]}"],
  "semana_str": "$SEMANA_STR"
}
EOF

# Limpar JSONs antigos de execuções anteriores
rm -f /tmp/clickup_raw_*.json

echo "Config salva:"
cat /tmp/entrega_config.json
```

Confirme que `prazo_ms` é um número razoável (13 dígitos, epoch em ms).

---

### ETAPA 2 — Buscar tarefas no ClickUp (7 chamadas, com paginação)

Para **cada dia** em `dias[]`, faça buscas usando `mcp__claude_ai_ClickUp__clickup_search`.
**Salve IMEDIATAMENTE cada resultado em arquivo JSON usando a ferramenta Write.**

```
Para cada DIA em dias[] (ex: "16/03", "17/03", ..., "22/03"):

  cursor = null
  pagina = 0

  LOOP_PAGINAÇÃO:
    resultado = mcp__claude_ai_ClickUp__clickup_search(
      keywords = "DD/MM"              ← dia atual (ex: "17/03")
      filters = {
        "asset_types": ["task"],
        "location": {
          "subcategories": ["901305832980", "900702180610", "901324888130"]
        }
      },
      count = 100,
      cursor = cursor                 ← null na primeira chamada
    )

    # ⚠️ IMEDIATAMENTE após receber o resultado:
    # Use a ferramenta Write para salvar em /tmp/clickup_raw_DD_MM_pN.json
    # (substitua DD_MM pelo dia sem barra, ex: 17_03; N = número da página)
    # O conteúdo deve ser o JSON completo do resultado (copie na íntegra)

    # Verificar paginação
    Se resultado contém "next_cursor" e next_cursor não é null/vazio:
      cursor = next_cursor
      pagina += 1
      Repetir LOOP_PAGINAÇÃO
    Senão:
      Próximo dia
```

**REGRAS CRÍTICAS:**
- Use a ferramenta **Write** (não Bash) para salvar cada JSON — evita problemas com caracteres especiais
- Nome do arquivo: `/tmp/clickup_raw_DD_MM_p0.json` (p0, p1, p2... para páginas)
- Se uma busca retornar 0 resultados, salve o JSON vazio e continue
- Se der erro de conexão, retry 1x antes de reportar falha
- **NÃO tente processar dados inline** — apenas salve e prossiga

Ao final você terá ~7 arquivos (ou mais se houver paginação):
`/tmp/clickup_raw_16_03_p0.json`, `/tmp/clickup_raw_17_03_p0.json`, etc.

---

### ETAPA 3 — Executar script Python de processamento

Após salvar TODOS os JSONs, execute o script:

```bash
python3 /Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/preencher_entregas_clickup.py
```

**Argumentos opcionais:**

| Argumento | Uso | Exemplo |
|-----------|-----|---------|
| `--semana` | Semana específica | `--semana "16/03 a 22/03"` |
| `--quarta` | Data da quarta de referência | `--quarta 2026-03-18` |
| `--mes` | Aba do mês na planilha | `--mes Março` |
| `--dry-run` | Apenas calcula, sem escrever | `--dry-run` |

O script faz automaticamente:
1. Lê os JSONs de `/tmp/clickup_raw_*.json`
2. Filtra subtasks da semana com assignees do time
3. Salva dados brutos na aba "Dados Brutos" do Google Sheets
4. Atualiza aba "Status" com timestamp e resultado
5. Calcula demandas e entregas no prazo por colaborador
6. Exibe tabela com resultados
7. Atualiza aba do mês na planilha de entregas (se não --dry-run)

---

## Erros comuns e como lidar

| Situação | Ação |
|----------|------|
| ClickUp MCP não disponível | Mostrar erro e pedir para verificar conexão MCP |
| Busca retorna 0 tarefas em todos os dias | Verificar se as listas IDs estão corretos |
| `next_cursor` presente na resposta | Continuar buscando até cursor ser null |
| Arquivo JSON corrompido | Script ignora e continua processando |
| `date_updated` ausente | Contar como entregue se status é de entrega |
| Assignee não está no TEAM | Ignorado pelo script |
| Tarefa sem assignees | Não conta para ninguém |
| Semana sem tarefas para alguém | Mostra "0  0  N/A" |
| Dados perdidos por compaction | **Impossível** — dados estão em `/tmp/*.json` |

---

## Dependências

| Componente | Tipo | Detalhes |
|------------|------|---------|
| ClickUp MCP | MCP Server | `mcp__claude_ai_ClickUp__clickup_search` |
| Google Sheets API | API | gspread + credentials.json |
| Python 3 | Runtime | Processa JSONs, salva no Sheets, calcula entregas |
| Fuso horário | Config | America/Bahia (UTC-3) |

---

## Status de integração

| Serviço | Status | Via |
|---------|--------|-----|
| ClickUp | Automático | MCP (`clickup_search`) |
| Google Sheets | Automático | Script Python (gspread) |
