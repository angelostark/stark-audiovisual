---
task: AV Entrega Semanal
agent: av-monitor
version: 1.0.0
elicit: false
mode: autonomous
---

# Task: av-entrega-semanal

Calcula a taxa de entrega de posts no prazo (segunda 00h a quarta 20h) para todos os membros do time audiovisual. Busca TODAS as tarefas da lista com paginacao completa.

## Inputs

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| `semana` | string | Nao | Semana especifica (ex: "24/03"). Default: semana atual |

## Preconditions

- [ ] ClickUp MCP disponivel
- [ ] Acesso a lista ID: 901324888130

## Steps

### Step 1: Calcular janela de tempo da semana

**CRITICO: Encontrar a SEGUNDA-FEIRA correta da semana.**

Para calcular a segunda-feira da semana atual:
```
hoje = data atual
dia_da_semana = dia da semana de hoje (0=domingo, 1=segunda, 2=terca, ..., 6=sabado)

SE dia_da_semana == 0 (domingo):
  segunda_inicio = hoje - 6 dias
SENAO:
  segunda_inicio = hoje - (dia_da_semana - 1) dias

quarta_limite  = segunda_inicio + 2 dias, 20:00:00 (America/Sao_Paulo)
domingo_fim    = segunda_inicio + 6 dias, 23:59:59 (America/Sao_Paulo)
```

**VALIDACAO OBRIGATORIA:** Antes de executar as consultas, confirmar:
- "Segunda-feira calculada: {segunda_inicio} — dia da semana: segunda-feira"
- SE o dia calculado NAO for segunda-feira → ERRO, recalcular

Converter para formato YYYY-MM-DD para uso nos filtros do ClickUp.

**Exemplo: se hoje e 24/03/2026 (terca-feira):**
- dia_da_semana = 2 (terca)
- segunda_inicio = 24 - (2-1) = 24 - 1 = **23/03/2026 (segunda)**
- quarta_limite = 23 + 2 = **25/03/2026 20:00 (quarta)**
- domingo_fim = 23 + 6 = **29/03/2026**
- due_date_from = "2026-03-23"
- due_date_to = "2026-03-29"

**Exemplo: se hoje e 26/03/2026 (quinta-feira):**
- dia_da_semana = 4 (quinta)
- segunda_inicio = 26 - (4-1) = 26 - 3 = **23/03/2026 (segunda)**
- quarta_limite = **25/03/2026 20:00**
- domingo_fim = **29/03/2026**

### Step 2: Buscar TODAS as tarefas da semana (com paginacao)

**CRITICO: Paginacao obrigatoria.** O ClickUp retorna no maximo 100 tarefas por pagina.

**Algoritmo de paginacao com retry:**

```
todas_tarefas = []
pagina = 0
MAX_RETRIES = 3
WAIT_SECONDS = [5, 10, 20]  // backoff progressivo

LOOP:
  tentativa = 0
  sucesso = false

  RETRY_LOOP:
    resultado = clickup_filter_tasks({
      list_ids: ["901324888130"],
      subtasks: true,
      include_closed: true,
      order_by: "due_date",
      due_date_from: "{segunda_inicio}",
      due_date_to: "{domingo_fim}",
      page: pagina
    })

    SE resultado retornou ERRO (502, timeout, MCP indisponivel, etc.):
      tentativa = tentativa + 1
      SE tentativa >= MAX_RETRIES:
        EXIBIR: "⚠️ Erro persistente na pagina {pagina} apos {MAX_RETRIES} tentativas. Aguardando 30s para ultima tentativa..."
        AGUARDAR 30 segundos
        resultado = clickup_filter_tasks(... mesmos params ...)
        SE resultado retornou ERRO:
          EXIBIR: "🔴 MCP indisponivel apos 4 tentativas. Dados parciais: {T} tarefas em {pagina} paginas."
          BREAK LOOP  // sair com dados parciais, mas SINALIZAR no output
        SENAO:
          sucesso = true
      SENAO:
        EXIBIR: "⏳ Erro temporario na pagina {pagina}. Tentativa {tentativa}/{MAX_RETRIES}. Aguardando {WAIT_SECONDS[tentativa]}s..."
        AGUARDAR WAIT_SECONDS[tentativa] segundos
        CONTINUAR RETRY_LOOP
    SENAO:
      sucesso = true

  SE sucesso:
    todas_tarefas.append(resultado.tasks)
    SE resultado.count < 100:
      BREAK  // ultima pagina
    SENAO:
      pagina = pagina + 1
      CONTINUAR LOOP
```

**REGRAS DE RETRY:**
- Erros temporarios (502, 503, timeout, "bad gateway", conexao recusada) → SEMPRE retry
- Espera progressiva: 5s → 10s → 20s → 30s (ultima chance)
- Maximo 4 tentativas por pagina (3 retries + 1 ultima chance)
- Se todas falharem: continuar com dados parciais, mas SINALIZAR CLARAMENTE no output
- NUNCA desistir na primeira falha — o MCP pode ter instabilidade momentanea

**Ao final, registrar:**
- Total de paginas consultadas
- Total de tarefas coletadas
- Retries ocorridos (se houver)
- Confirmar: "Paginacao completa: {N} paginas, {T} tarefas totais" ou "Paginacao parcial: {N} paginas, {T} tarefas (erro na pagina {X})"

### Step 3: Buscar tarefas concluidas no prazo (segunda a quarta 20h)

**Segunda consulta com filtro por data de conclusao (mesmo mecanismo de retry do Step 2):**

```
tarefas_concluidas = []
pagina = 0
MAX_RETRIES = 3
WAIT_SECONDS = [5, 10, 20]

LOOP:
  tentativa = 0
  sucesso = false

  RETRY_LOOP:
    resultado = clickup_filter_tasks({
      list_ids: ["901324888130"],
      subtasks: true,
      include_closed: true,
      date_done_from: "{segunda_inicio}",
      date_done_to: "{quarta_limite}",
      page: pagina
    })

    SE resultado retornou ERRO:
      tentativa = tentativa + 1
      SE tentativa >= MAX_RETRIES:
        AGUARDAR 30 segundos  // ultima chance
        resultado = clickup_filter_tasks(... mesmos params ...)
        SE resultado retornou ERRO:
          BREAK LOOP com dados parciais
        SENAO:
          sucesso = true
      SENAO:
        EXIBIR: "⏳ Retry {tentativa}/{MAX_RETRIES} na pagina {pagina}. Aguardando {WAIT_SECONDS[tentativa]}s..."
        AGUARDAR WAIT_SECONDS[tentativa] segundos
        CONTINUAR RETRY_LOOP
    SENAO:
      sucesso = true

  SE sucesso:
    tarefas_concluidas.append(resultado.tasks)
    SE resultado.count < 100:
      BREAK
    SENAO:
      pagina = pagina + 1
      CONTINUAR LOOP
```

### Step 4: Contar tarefas por membro (consulta individual — DADOS EXATOS)

**CRITICO: NAO contar manualmente a partir da paginacao geral.**
Usar o filtro `assignees` do ClickUp para obter contagem EXATA por membro.

Para cada membro em `data/av-team-config.yaml` (designers + editores):

```
membros = [
  {id: "84856123",  nome: "Eloy Lopes"},
  {id: "82154730",  nome: "Humberto Sales"},
  {id: "112104837", nome: "Max Ayalla"},
  {id: "106172497", nome: "Milena Araujo"},
  {id: "248549658", nome: "Mateus Deckmann"},
  {id: "188585120", nome: "Ebertty Matnai"},
  {id: "112104835", nome: "Joao Andare"},
  {id: "82029622",  nome: "Andre Araujo"}
]

Para cada membro:
  resultado = clickup_filter_tasks({
    list_ids: ["901324888130"],
    assignees: [membro.id],
    subtasks: true,
    include_closed: true,
    order_by: "due_date",
    due_date_from: "{segunda_inicio}",
    due_date_to: "{quarta_limite}",
    page: 0
  })

  // Aplicar mesmo mecanismo de retry em caso de erro

  membro.total = resultado.count  // ESTE E O NUMERO EXATO DO CLICKUP

  // Contar status a partir das tarefas retornadas
  membro.concluidas = count(tarefas onde status in ["edicao concluida", "concluido"])
  membro.em_edicao = count(tarefas onde status = "edicao")
  membro.a_fazer = count(tarefas onde status = "a ser feito")
  membro.outros = membro.total - membro.concluidas - membro.em_edicao - membro.a_fazer

  membro.pct_entrega = (membro.concluidas / membro.total) * 100  // 0 se total = 0

  // SE resultado.count == 100: paginar para obter TODAS as tarefas do membro
  SE resultado.count == 100:
    pagina = 1
    LOOP:
      resultado_extra = clickup_filter_tasks({
        ...mesmos params...,
        page: pagina
      })
      acumular tarefas e recontar status
      SE resultado_extra.count < 100: BREAK
      pagina = pagina + 1
```

**POR QUE consulta individual?**
- O filtro `assignees` do ClickUp retorna o `count` exato
- Contar manualmente em 700+ tarefas paginadas gera erro de ~5-10%
- Uma consulta por membro (8 consultas) e mais preciso que contar em 8 paginas

**VALIDACAO:** O total por membro DEVE bater com o numero mostrado no ClickUp.
Se nao bater, investigar se ha tarefas com due_date fora do range ou subtasks nao incluidas.

**Status das tarefas para classificacao:**
- **ENTREGUE NO PRAZO**: status in ["edicao concluida", "concluido"] E date_done <= quarta 20h
- **ENTREGUE ATRASADO**: status in ["edicao concluida", "concluido"] E date_done > quarta 20h
- **EM ANDAMENTO**: status in ["edicao", "revisao"]
- **NAO INICIADO**: status = "a ser feito"
- **SEM RESPONSAVEL**: assignees = []

**PARALELISMO:** As 8 consultas por membro sao independentes — podem ser executadas em paralelo para maior velocidade.

### Step 5: Calcular metricas gerais

```
// Somar os totais exatos dos 8 membros (Step 4)
total_tarefas_membros = soma(membro.total para cada membro)
total_concluidas = soma(membro.concluidas para cada membro)
total_em_edicao = soma(membro.em_edicao para cada membro)
total_a_fazer = soma(membro.a_fazer para cada membro)
total_outros = soma(membro.outros para cada membro)

// Tarefas sem responsavel vem do Step 2 (paginacao geral)
total_sem_responsavel = count(tarefas em todas_tarefas onde assignees = [])

// Taxa geral
pct_entrega_geral = (total_concluidas / total_tarefas_membros) * 100
```

**NOTA:** O total geral da paginacao (Step 2) inclui tarefas de coordenadores e outros membros
nao listados nos 8 membros principais. O total por membro e a fonte de verdade para o relatorio.

### Step 6: Montar e exibir output

Usar template de output abaixo.

## Output Format

```markdown
## 📦 Entrega Semanal — Agenda de Postagem 3.0
**Semana:** DD/MM a DD/MM/YYYY
**Data da consulta:** DD/MM/YYYY HH:MM
**Janela de entrega:** Segunda 00h a Quarta 20h
**Paginacao:** {N} paginas consultadas | {T} tarefas totais coletadas

### Resumo Geral
| Metrica | Qtd | % |
|---------|-----|---|
| Total de tarefas da semana | N | 100% |
| Entregues no prazo (ate qua 20h) | N | N% |
| Entregues com atraso (apos qua 20h) | N | N% |
| Em andamento | N | N% |
| Nao iniciado | N | N% |
| Sem responsavel | N | — |

**Taxa de entrega no prazo:** N%

### Por Membro — Designers
| Membro | Total | No prazo | Atrasado | Andamento | Pendente | % Entrega |
|--------|-------|----------|----------|-----------|----------|-----------|
| Eloy Lopes | N | N | N | N | N | N% |
| Humberto Sales | N | N | N | N | N | N% |
| Max Ayalla | N | N | N | N | N | N% |
| Milena Araujo | N | N | N | N | N | N% |
| Mateus Deckmann | N | N | N | N | N | N% |

### Por Membro — Editores
| Membro | Total | No prazo | Atrasado | Andamento | Pendente | % Entrega |
|--------|-------|----------|----------|-----------|----------|-----------|
| Ebertty Matnai | N | N | N | N | N | N% |
| Joao Andare | N | N | N | N | N | N% |
| Andre Araujo | N | N | N | N | N | N% |

### Por Membro — Coordenadores/Estrategistas
| Membro | Total | No prazo | Atrasado | Andamento | Pendente | % Entrega |
|--------|-------|----------|----------|-----------|----------|-----------|
| Matheus Peleteiro | N | N | N | N | N | N% |
| Bruna Santana | N | N | N | N | N | N% |
| Thaynara Castro | N | N | N | N | N | N% |
| Evany Bandeira | N | N | N | N | N | N% |
| Daniela Cabral | N | N | N | N | N | N% |
| Germana Souza | N | N | N | N | N | N% |
| Gabriella Andrade | N | N | N | N | N | N% |

### Tarefas sem responsavel
| Tarefa | Due Date | Status |
|--------|----------|--------|
| [nome da tarefa] | DD/MM | status |

---
*Dados completos — {N} paginas paginadas, {T} tarefas analisadas.*
*Use `*status-semanal` para visao geral ou `*atrasados` para detalhar atrasos.*
```

## Veto Conditions

- **VETO** se ClickUp MCP nao responder na PRIMEIRA pagina mesmo apos todos os retries → "Nao foi possivel acessar o ClickUp apos multiplas tentativas. Verifique a conexao MCP."
- **VETO** se lista retornar 0 tarefas → "Lista vazia ou ID incorreto. Verificar configuracao."
- **NUNCA** parar na primeira pagina se count == 100 (indica mais paginas)
- **NUNCA** desistir no primeiro erro — SEMPRE fazer retry com backoff progressivo
- **SE** dados parciais (erro apos pagina N): exibir relatorio com aviso claro "⚠️ DADOS PARCIAIS — erro na pagina {N+1} apos 4 tentativas. Re-execute para dados completos."
- **NUNCA** apresentar dados parciais como se fossem completos

## Completion Criteria

- [ ] Calculou janela de tempo correta (segunda 00h a quarta 20h)
- [ ] Paginacao completa: buscou TODAS as paginas ate count < 100
- [ ] Retry automatico em erros temporarios (502, timeout, etc.) com backoff 5s→10s→20s→30s
- [ ] Registrou total de paginas, tarefas coletadas e retries ocorridos
- [ ] Se dados parciais: sinalizou claramente no output com aviso "DADOS PARCIAIS"
- [ ] Filtrou tarefas concluidas dentro do prazo (date_done <= quarta 20h)
- [ ] Consulta INDIVIDUAL por membro via filtro `assignees` (8 consultas, contagem exata)
- [ ] Total por membro BATE com o ClickUp (count do resultado = numero real)
- [ ] Calculou % de entrega por membro (designers + editores)
- [ ] Identificou tarefas sem responsavel
- [ ] Exibiu tabela completa com todos os membros do time
