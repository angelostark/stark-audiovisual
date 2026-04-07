---
name: preencher-entrega-posts
description: >
  Calcula a % de entrega de posts no prazo (até quarta 20h) para cada
  designer/editor do time Audiovisual da Stark. Busca do ClickUp via MCP,
  usa timestamps precisos (bulk_time_in_status), e atualiza planilha de entregas.

  Use SEMPRE que o usuário pedir: "preencher entrega de posts", "verificar entregas",
  "calcular entregas da semana", "meta de entrega", "prazo de entrega posts",
  "rodar entrega posts", ou qualquer variação de verificar/calcular/preencher
  entregas de posts do time audiovisual.
---

# Preencher Entrega de Posts — Stark Audiovisual (v2)

Essa skill busca tarefas do ClickUp via MCP, obtém timestamps precisos de entrega
via `bulk_time_in_status`, e atualiza a planilha com dados reais de quando cada
tarefa foi concluída vs o prazo de quarta 20h.

> **REGRA CRÍTICA:** Salve TODOS os resultados de busca em arquivos JSON imediatamente
> após cada chamada. NÃO dependa do contexto inline — ele será perdido no compaction.
> Processe os dados via script Python, nunca inline.

---

## Arquitetura

```
Skill → ClickUp MCP (filter_tasks + bulk_time_in_status)
     → /tmp/clickup_filter_week*.json + /tmp/clickup_bulk_status_*.json
     → Python (processar_entregas_raw.py) → entregas_calculadas.json
     → Python (preencher_entregas_clickup.py --input) → Google Sheets
```

---

## Constantes

### Planilha
```
SHEET_ID = "1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA"
```
- Aba "Dados Brutos" → dados crus
- Aba "Status" → timestamp da última execução
- Aba do mês (Janeiro, Fevereiro, Março...) → resultado de entregas

### Lista ClickUp
```
LIST_ID = "901324888130"  # Agenda de Postagem 3.0
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

### ETAPA 1 — Calcular semanas do mês e salvar config

Determine as semanas do mês alvo e salve em `/tmp/entregas_weeks_config.json`.

**Regras para definir semanas:**
- Uma semana vai de segunda a domingo
- Se a segunda-feira cai no mês alvo, a semana pertence ao mês
- Prazo de cada semana: quarta-feira da mesma semana às 20:00 (America/Bahia, UTC-3)

Use Bash para calcular:

```bash
export TZ="America/Bahia"

# Mês/ano alvo (padrão: mês atual)
MES=$(date +%m)
ANO=$(date +%Y)
MES_NOME=$(python3 -c "meses=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']; print(meses[int('$MES')-1])")

# Limpar dados antigos
rm -f /tmp/clickup_filter_week*.json /tmp/clickup_bulk_status_*.json /tmp/entregas_calculadas.json

echo "Mes: $MES_NOME $ANO"
```

Em seguida, use Python para gerar a config de semanas:

```bash
python3 -c "
import json
from datetime import datetime, timedelta

mes = int('$MES')
ano = int('$ANO')
mes_nome = '$MES_NOME'

# Encontrar primeira segunda-feira do mês ou antes
primeiro_dia = datetime(ano, mes, 1)
# Recuar até a segunda-feira mais recente
weekday = primeiro_dia.weekday()  # 0=seg, 6=dom
if weekday != 0:
    primeira_seg = primeiro_dia - timedelta(days=weekday)
else:
    primeira_seg = primeiro_dia

# Se a segunda está no mês anterior, só inclui se terça+ está no mês
if primeira_seg.month != mes:
    primeira_seg = primeiro_dia + timedelta(days=(7 - weekday) % 7)

semanas = []
seg = primeira_seg
week_num = 1
while seg.month == mes or (seg + timedelta(days=6)).month == mes:
    if seg.month != mes and seg.day > 7:
        break
    if seg.month == mes:
        quarta = seg + timedelta(days=2)
        domingo = seg + timedelta(days=6)
        deadline_ms = int(datetime(quarta.year, quarta.month, quarta.day, 20, 0, 0).timestamp() * 1000)
        semana_str = f\"{seg.strftime('%d/%m')} a {domingo.strftime('%d/%m')}\"
        semanas.append({
            'week_num': week_num,
            'segunda': seg.strftime('%Y-%m-%d'),
            'domingo': domingo.strftime('%Y-%m-%d'),
            'quarta': quarta.strftime('%Y-%m-%d'),
            'deadline_ms': deadline_ms,
            'semana_str': semana_str,
        })
        week_num += 1
    seg += timedelta(days=7)

config = {'mes': mes_nome, 'ano': ano, 'semanas': semanas}
with open('/tmp/entregas_weeks_config.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f'Config salva: {len(semanas)} semanas')
for s in semanas:
    print(f'  Semana {s[\"week_num\"]}: {s[\"semana_str\"]} (deadline: {s[\"quarta\"]} 20h)')
"
```

Confirme que as semanas e deadlines estão corretas antes de prosseguir.

---

### ETAPA 2 — Buscar tarefas por semana (filter_tasks)

Para **cada semana**, busque TODAS as tarefas da lista com paginação.
**NÃO filtre por membro** — busque tudo de uma vez e filtre depois.

```
Para cada SEMANA (week_num, segunda, domingo):

  page = 0

  LOOP_PAGINACAO:
    resultado = mcp__claude_ai_ClickUp__clickup_filter_tasks(
      list_ids = ["901324888130"],
      subtasks = true,
      include_closed = true,
      due_date_from = "{segunda}",
      due_date_to = "{domingo}",
      page = page
    )

    # ⚠️ IMEDIATAMENTE salvar com Write:
    # /tmp/clickup_filter_week{week_num}_p{page}.json

    # Verificar se há mais páginas
    # Se retornou exatamente 100 tarefas (count=100), há mais páginas:
    Se count == 100:
      page += 1
      Repetir LOOP_PAGINACAO
    Senão:
      Próxima semana
```

**REGRAS:**
- Use a ferramenta **Write** para salvar cada resultado JSON completo
- Nome: `/tmp/clickup_filter_week{N}_p{page}.json`
- Se retornar 0 tarefas, salve o JSON e continue
- **PARALELISMO:** Pode buscar semanas em paralelo (até 4 chamadas simultâneas)
- Se der erro, retry 1x com backoff de 3s

**Exemplo com 4 semanas (sem paginação):**
```
/tmp/clickup_filter_week1_p0.json
/tmp/clickup_filter_week2_p0.json
/tmp/clickup_filter_week3_p0.json
/tmp/clickup_filter_week4_p0.json
```

---

### ETAPA 3 — Buscar timestamps precisos (bulk_time_in_status)

Após salvar TODOS os filter_tasks, colete os IDs das tarefas entregues
e busque os timestamps exatos de quando cada tarefa mudou para status de entrega.

```
# 1. Ler todos os /tmp/clickup_filter_week*.json
# 2. Coletar task_ids onde:
#    - status está em STATUS_ENTREGUE
#    - tem pelo menos 1 assignee com UID no TEAM

# 3. Dividir em lotes de 100 (limite da API)
# 4. Para cada lote:

    resultado = mcp__claude_ai_ClickUp__clickup_get_bulk_tasks_time_in_status(
      task_ids = [lista de até 100 IDs]
    )

    # ⚠️ IMEDIATAMENTE salvar:
    # /tmp/clickup_bulk_status_{batch_num}.json
```

**REGRAS:**
- Leia os JSONs salvos na ETAPA 2 para coletar os IDs
- Máximo 100 IDs por chamada de bulk_time_in_status
- Se der erro em um lote, retry 1x antes de pular
- Salve CADA resultado em arquivo separado
- **NÃO processe timestamps inline** — o Python faz isso

**Exemplo com 250 tarefas entregues:**
```
/tmp/clickup_bulk_status_0.json  (IDs 1-100)
/tmp/clickup_bulk_status_1.json  (IDs 101-200)
/tmp/clickup_bulk_status_2.json  (IDs 201-250)
```

---

### ETAPA 4 — Executar scripts Python de processamento

Após salvar TODOS os JSONs, execute o processamento:

```bash
# Passo 1: Processar dados brutos e gerar entregas_calculadas.json
python3 /Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/processar_entregas_raw.py --write
```

O script `processar_entregas_raw.py` faz:
1. Lê `/tmp/entregas_weeks_config.json` (config de semanas)
2. Lê `/tmp/clickup_filter_week*.json` (tarefas por semana)
3. Lê `/tmp/clickup_bulk_status_*.json` (timestamps)
4. Calcula demandas e entregas no prazo por membro/semana
5. Salva `/tmp/entregas_calculadas.json`
6. Com `--write`: chama `preencher_entregas_clickup.py --input` para escrever na planilha

**Para dry-run (sem escrever na planilha):**
```bash
python3 /Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/processar_entregas_raw.py --write --dry-run
```

---

## Erros comuns e como lidar

| Situação | Ação |
|----------|------|
| ClickUp MCP não disponível | Mostrar erro e pedir para verificar conexão MCP |
| filter_tasks retorna 0 em todas as semanas | Verificar LIST_ID e datas |
| count=100 na resposta | Paginar: buscar page+1 |
| bulk_status falha em um lote | Retry 1x, se falhar salva JSON vazio e continua |
| Membro sem tarefas na semana | Aparece com 0/0, ignorado na planilha |
| Dados perdidos por compaction | **Impossível** — tudo salvo em /tmp/*.json |

---

## Dependências

| Componente | Tipo | Detalhes |
|------------|------|---------|
| ClickUp MCP | MCP Server | `clickup_filter_tasks` + `clickup_get_bulk_tasks_time_in_status` |
| Google Sheets API | API | gspread + credentials.json |
| Python 3 | Runtime | processar_entregas_raw.py + preencher_entregas_clickup.py |
| Fuso horário | Config | America/Bahia (UTC-3) |

---

## Automação (quarta 20h)

Essa skill pode rodar automaticamente toda quarta-feira às 20h via:
- **LaunchAgent:** `~/Library/LaunchAgents/com.stark.preencher-entregas.plist`
- **Wrapper:** `automacoes/run_preencher_entregas.sh`
- **Claude CLI:** Executa a skill com `--dangerously-skip-permissions`
