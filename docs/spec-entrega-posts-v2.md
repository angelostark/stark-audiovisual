# Spec: Reestruturação Entrega de Posts v2

**Autor:** Morgan (PM) | **Data:** 2026-03-22
**Solicitante:** Ângelo Gabriel | **Status:** Em revisão

---

## 1. Visão Geral

Separar a coleta de dados (ClickUp) do processamento (cálculo de entregas), usando Make.com como intermediário que alimenta uma planilha Google Sheets semanalmente.

### Arquitetura Antes vs Depois

```
ANTES:
  Skill → ClickUp MCP (7 buscas) → /tmp/*.json → Python → Terminal + Planilha

DEPOIS:
  Make.com (Quarta 20h) → ClickUp API → Google Sheets "Dados Brutos"
  Skill (sob demanda)   → Google Sheets → Python → Terminal + Planilha Entregas
```

### Benefícios
- Skill roda em 5 segundos (lê planilha) ao invés de 2-3 minutos (7 buscas ClickUp)
- Dados persistem na planilha (não dependem de /tmp/ ou contexto)
- Make.com pode ser monitorado/debugado separadamente
- Elimina problemas de paginação e compaction do contexto

---

## 2. Cenário Make.com — Spec Completo

### 2.1. Configuração Geral

| Campo | Valor |
|-------|-------|
| **Nome** | `Entrega de Posts - Coleta Semanal` |
| **Agendamento** | Toda quarta-feira às 20:00 (America/Bahia, UTC-3) |
| **Timeout** | 40 minutos |

### 2.2. Fluxo de Módulos

```
[1] Variáveis    → Calcular datas da semana
[2] ClickUp x3  → Buscar tarefas das 3 listas
[3] Aggregator   → Combinar resultados
[4] Iterator     → Iterar cada tarefa
[5] Filter       → Filtrar subtasks válidas da semana
[6] Google Sheets → Limpar aba + Inserir linhas
```

### 2.3. Módulo 1 — Calcular Datas (Set Multiple Variables)

Variáveis a criar:

| Variável | Fórmula Make.com | Exemplo |
|----------|-----------------|---------|
| `segunda` | `addDays(now; -(formatDate(now; "E") - 1))` | `2026-03-16` |
| `domingo` | `addDays(segunda; 6)` | `2026-03-22` |
| `quarta_prazo` | `addDays(segunda; 2)` | `2026-03-18` |
| `semana_str` | `formatDate(segunda; "DD/MM") & " a " & formatDate(domingo; "DD/MM")` | `16/03 a 22/03` |
| `dias_busca` | Array com 7 strings DD/MM | `["16/03","17/03",...,"22/03"]` |

> **Nota:** No Make.com use `setVar` ou módulo "Tools > Set multiple variables"

### 2.4. Módulo 2 — Buscar Tarefas do ClickUp (x3)

Usar o módulo **ClickUp > Search Tasks** (ou HTTP request se o módulo nativo não suportar filtros avançados).

**Repetir para cada lista:**

| Lista | ID |
|-------|-----|
| Posts do Insta 2.0 | `901305832980` |
| Edição de Vídeos 2.1 | `900702180610` |
| Agenda de Postagem 3.0 | `901324888130` |

**Configuração de cada módulo ClickUp:**

```
Método: GET
URL: https://api.clickup.com/api/v2/list/{LIST_ID}/task
Query params:
  - subtasks: true
  - include_closed: true
  - page: 0 (paginar se houver mais de 100)
  - order_by: updated
  - date_updated_gt: {{toTimestamp(segunda)}}000

Headers:
  - Authorization: {CLICKUP_API_KEY}
```

> **Alternativa simplificada:** Se a API de busca do ClickUp suportar, use `GET /team/{TEAM_ID}/task` com filtros por lista. Mas o endpoint por lista é mais confiável.

**Paginação:** O ClickUp retorna `last_page: true/false`. Se `false`, incrementar `page` e repetir.

### 2.5. Módulo 3 — Aggregator

Combinar os resultados das 3 listas em um array único de tarefas.

### 2.6. Módulo 4+5 — Iterator + Filter

**Iterator:** Percorre cada tarefa do array combinado.

**Filter (condições AND):**
1. `task.parent` existe (é subtask) — OU `task.hierarchy.task` existe
2. Nome da tarefa OU nome da tarefa pai contém pelo menos um dos `dias_busca`
3. Pelo menos um `assignee.id` está na lista do time:
   ```
   [82154730, 112104835, 84856123, 112104837, 106090854, 106172497, 188585120, 82029622, 248549658]
   ```

### 2.7. Módulo 6 — Google Sheets

**Passo 6a — Limpar aba "Dados Brutos":**
- Módulo: Google Sheets > Delete Rows
- Deletar todas as linhas da aba "Dados Brutos" EXCETO o header (linha 1)

**Passo 6b — Inserir linhas:**
- Módulo: Google Sheets > Add a Row
- Uma linha por tarefa filtrada, uma linha por assignee (se múltiplos assignees, duplicar a linha)

**Mapeamento de colunas:**

| Coluna | Header | Fonte | Formato |
|--------|--------|-------|---------|
| A | `semana` | Variável `semana_str` | Texto: `16/03 a 22/03` |
| B | `task_id` | `task.id` | Texto |
| C | `task_name` | `task.name` | Texto |
| D | `status` | `task.status.status` | Texto lowercase |
| E | `date_updated` | `task.date_updated` | Número (epoch ms) |
| F | `assignee_uid` | `assignee.id` | Número |
| G | `assignee_name` | `assignee.username` | Texto |
| H | `parent_name` | `task.parent.name` ou nome da tarefa pai | Texto |
| I | `list_id` | `task.list.id` | Texto |
| J | `date_created` | `task.date_created` | Número (epoch ms) |

### 2.8. Tratamento de Erros

- Se a API do ClickUp retornar erro 429 (rate limit): aguardar 60s e tentar novamente
- Se Google Sheets falhar: enviar notificação por email para angelo@starkmkt.com
- Guardar log da execução no Make.com

### 2.9. Time do ClickUp (referência para mapeamento)

| UID | Nome |
|-----|------|
| 82154730 | Humberto |
| 112104835 | João |
| 84856123 | Eloy |
| 112104837 | Max |
| 106090854 | Karyne |
| 106172497 | Milena |
| 188585120 | Ebertty |
| 82029622 | André |
| 248549658 | Mateus Redman |

---

## 3. Google Sheets — Estrutura da Planilha Nova

### 3.1. Informações

| Campo | Valor |
|-------|-------|
| **Nome** | `Dados Entregas AV - Raw` |
| **Compartilhar com** | Service account do credentials.json + angelo@starkmkt.com |

### 3.2. Aba "Dados Brutos"

Header na linha 1, dados a partir da linha 2:

```
A: semana | B: task_id | C: task_name | D: status | E: date_updated | F: assignee_uid | G: assignee_name | H: parent_name | I: list_id | J: date_created
```

**Regras:**
- O Make.com LIMPA esta aba toda quarta antes de inserir (dados sempre frescos da semana atual)
- Se precisar de histórico, o Make.com pode manter uma aba "Histórico" separada (append-only)

### 3.3. Aba "Histórico" (opcional, recomendado)

Mesma estrutura da aba "Dados Brutos", mas nunca limpa. O Make.com faz append toda semana. Permite consultar semanas anteriores.

### 3.4. Aba "Status" (obrigatória — usada pelo sistema de notificação)

Header na linha 1, dados na linha 2 (sobrescritos a cada execução):

| Coluna | Header | Conteúdo |
|--------|--------|----------|
| A | `timestamp` | Data/hora ISO da execução (ex: `2026-03-18T20:05:32`) |
| B | `status` | `OK` ou `FALHA` |
| C | `tasks_count` | Número de tarefas gravadas na aba Dados Brutos |
| D | `error_message` | Vazio se OK, mensagem de erro se FALHA |

**No Make.com:**
- No final do cenário (sucesso): módulo Google Sheets → Update Row na aba "Status", linha 2: `[now, "OK", count, ""]`
- No error handler (falha): módulo Google Sheets → Update Row na aba "Status", linha 2: `[now, "FALHA", 0, "{{error.message}}"]`

---

## 4. Notificação de Falha no Mac (LaunchAgent)

### 4.1. Como funciona

```
Make.com (Quarta 20h)  → Grava status na aba "Status" do Sheets
LaunchAgent (Quinta 9h) → Lê aba "Status" → Se FALHA ou desatualizado → Notificação macOS
```

### 4.2. Arquivos criados

| Arquivo | Caminho | Função |
|---------|---------|--------|
| Script de checagem | `automacoes/check_makecom_status.py` | Lê aba "Status", valida, dispara notificação |
| LaunchAgent | `~/Library/LaunchAgents/com.stark.check-makecom-entregas.plist` | Agenda execução quinta 9h |

### 4.3. O que o script checa

| Cenário | Ação |
|---------|------|
| Status = `FALHA` | Notificação com som: "Make.com falhou na quarta! Erro: ..." |
| Última execução > 48h atrás | Notificação com som: "Make.com não rodou há Xh" |
| Status = `OK` | Notificação silenciosa: "Make.com OK — N tarefas coletadas" |
| Aba "Status" vazia | Notificação: "Make.com nunca rodou" |

### 4.4. Ativar o LaunchAgent

```bash
launchctl load ~/Library/LaunchAgents/com.stark.check-makecom-entregas.plist
```

### 4.5. Testar manualmente

```bash
python3 automacoes/check_makecom_status.py
```

### 4.6. Configuração necessária

Editar `automacoes/check_makecom_status.py` linha 18 — substituir `PLACEHOLDER_SHEET_ID` pelo ID real da planilha nova.

---

## 5. Skill Reescrita — Novo Fluxo

### 4.1. O que muda

| Antes | Depois |
|-------|--------|
| 7 buscas ClickUp via MCP | 0 buscas — lê do Google Sheets |
| Salva JSONs em /tmp/ | Não precisa de /tmp/ |
| Script Python complexo com parsing JSON | Script Python simples lê planilha |
| 2-3 minutos para rodar | ~10 segundos |
| Depende de MCP ClickUp ativo | Depende apenas de Google Sheets API |

### 4.2. Novo passo a passo da skill

```
ETAPA 1 — Executar script Python
  python3 /path/to/preencher_entregas_clickup.py [--semana "16/03 a 22/03"] [--dry-run]

ETAPA 2 — Exibir resultado no terminal

Fim.
```

### 4.3. O que o script Python faz (nova versão)

1. Autenticar com Google Sheets via credentials.json
2. Abrir planilha "Dados Entregas AV - Raw"
3. Ler aba "Dados Brutos"
4. Filtrar pela semana atual (ou --semana especificada)
5. Calcular: para cada assignee_uid do TEAM
   - Total de demandas = count de linhas
   - Entregues no prazo = count onde status ∈ STATUS_ENTREGUE E date_updated <= quarta 20h
6. Calcular percentuais
7. Exibir tabela no terminal
8. Se não --dry-run: atualizar planilha de entregas existente (1qdAeM...)

---

## 5. Checklist de Implementação

### Make.com
- [ ] Criar cenário no Make.com
- [ ] Conectar conta ClickUp (API key)
- [ ] Conectar Google Sheets (OAuth ou service account)
- [ ] Configurar os 3 módulos de busca por lista
- [ ] Configurar filtros (subtask, dias, assignees)
- [ ] Configurar escrita na aba "Dados Brutos"
- [ ] Configurar escrita na aba "Status" (sucesso e erro)
- [ ] Testar com dados reais
- [ ] Agendar para quarta 20h America/Bahia

### Google Sheets
- [ ] Criar planilha "Dados Entregas AV - Raw"
- [ ] Criar aba "Dados Brutos" com headers (A-J)
- [ ] Criar aba "Status" com headers (A-D)
- [ ] (Opcional) Criar aba "Histórico"
- [ ] Compartilhar com service account
- [ ] Anotar o Sheet ID para o script e o checker

### Skill + Script
- [ ] Reescrever `preencher-entrega-posts.md`
- [ ] Atualizar `preencher_entregas_clickup.py`
- [ ] Testar com --dry-run
- [ ] Testar escrita na planilha de entregas

### Notificação Mac
- [ ] Atualizar `PLACEHOLDER_SHEET_ID` em `check_makecom_status.py`
- [ ] Carregar LaunchAgent: `launchctl load ~/Library/LaunchAgents/com.stark.check-makecom-entregas.plist`
- [ ] Testar manualmente: `python3 automacoes/check_makecom_status.py`

---

## 6. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Make.com não roda (falha/manutenção) | Skill não tem dados | LaunchAgent notifica quinta 9h + aba "Status" permite diagnóstico |
| Rate limit do ClickUp API | Coleta incompleta | Implementar retry com backoff no Make.com |
| Planilha fica sem dados em semana atípica | Skill mostra 0% | Skill deve avisar quando planilha está vazia |
| Mudança no time (novo membro) | Dados incompletos | Atualizar TEAM na skill E no filtro do Make.com |

---

*— Morgan, planejando o futuro*
