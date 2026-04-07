---
task: AV Metas Mensal
agent: av-monitor
version: 2.0.0
elicit: true
mode: interactive
---

# Task: av-metas

Calcula KPIs mensais do time audiovisual, grava na planilha de metas e envia DMs individuais via ClickUp Chat. O agente orquestra tudo — ClickUp MCP para Prazo de Entrega, Google Sheets para demais KPIs.

## Inputs

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| `mes` | int | Nao | Mes alvo (1-12). Default: mes atual |
| `ano` | int | Nao | Ano alvo. Default: ano atual |
| `mes-anterior` | flag | Nao | Processa o mes anterior ao atual |
| `skip-chat` | flag | Nao | Pula envio de DMs no ClickUp Chat |

## Elicitacao

Se nenhum parametro fornecido, perguntar:
```
Qual periodo deseja calcular as metas?

1. Mes atual
2. Mes anterior
3. Mes especifico (informar mes e ano)

Digite a opcao:
```

## Preconditions

- [ ] ClickUp MCP disponivel (para KPI Prazo de Entrega)
- [ ] Python 3.9+ com `gspread` e `google-auth` (para ler/escrever planilhas)
- [ ] Credenciais Google: `automacoes/credentials.json`
- [ ] (Opcional) ClickUp Chat MCP ou `CLICKUP_API_KEY` para DMs

## Dados do Time

Carregar `data/av-team-config.yaml` para IDs e roles.

**Designers:** Eloy (84856123), Humberto (82154730), Max (112104837), Milena (106172497), Joao (112104835), Karyne (106090854)
**Editores:** Ebertty (188585120), Mateus (248549658), Andre (82029622)

---

## Steps

### Step 1: Determinar periodo

Calcular:
- `mes_nome`: nome do mes em portugues (Janeiro, Fevereiro, ...)
- `mes_idx`: indice 1-12
- `ano`: ano alvo
- `semanas`: lista de todas as segundas-feiras do mes (para calcular janelas semanais)

```
Para cada semana que INTERSECTA o mes:
  segunda = primeira segunda-feira da semana
  quarta_limite = segunda + 2 dias, 20:00:00 (America/Sao_Paulo)
  domingo = segunda + 6 dias, 23:59:59
```

**Exemplo: Marco 2026**
- Semana 1: 02/03 (seg) a 08/03 (dom) → quarta 04/03 20h
- Semana 2: 09/03 a 15/03 → quarta 11/03 20h
- Semana 3: 16/03 a 22/03 → quarta 18/03 20h
- Semana 4: 23/03 a 29/03 → quarta 25/03 20h
- Semana 5: 30/03 a 31/03 (parcial) → quarta 01/04 20h (inclui se seg/ter caem no mes)

### Step 2: KPI — Prazo de Entrega (via ClickUp MCP)

**ESTE E O KPI QUE ERA MANUAL — AGORA AUTOMATIZADO VIA CLICKUP MCP.**

Para CADA SEMANA do mes, para CADA MEMBRO do time:

```
resultado = clickup_filter_tasks({
  list_ids: ["901324888130"],
  assignees: ["{membro.id}"],
  subtasks: true,
  include_closed: true,
  due_date_from: "{segunda}",
  due_date_to: "{domingo}",
  page: 0
})
```

**Contar por membro:**
- `total_demandas`: resultado.count (total de tarefas atribuidas na semana)
- `entregues_no_prazo`: tarefas com status in ["edicao concluida", "concluido", "aguardando postagem", "aprovado", "arte aprovada", "finalizado"] E (date_done <= quarta 20h OU date_updated <= quarta 20h)

**RETRY:** Mesmo protocolo do `av-entrega-semanal.md` — 3 retries com backoff 5s→10s→20s.

**Agregar mensal por pessoa (REGRA OFICIAL):**
```
Para cada semana: pct_semana = entregues / total
prazo_mensal[membro] = media(pct_semana1, pct_semana2, ..., pct_semanaN)
```
**ATENCAO:** E a MEDIA DAS PORCENTAGENS semanais, NAO soma(entregues)/soma(total).

Se `total_demandas == 0` para um membro em todas as semanas → `prazo = 0.0`

**FONTE DE VERDADE:** A planilha de Entregas (`1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA`).
Os dados semanais DEVEM estar preenchidos la antes de calcular o mensal.

**PARALELISMO:** Consultas por membro sao independentes — executar em paralelo quando possivel.

**VALIDACAO:** Exibir para cada membro:
```
  Eloy: Sem1(88.89%) + Sem2(78.43%) + Sem3(70.00%) + Sem4(92.68%) → media = 82.50%
```

### Step 3: KPI — Novos Modelos de Layout (via Google Sheets)

Ler planilha de Layouts (`18IYDy4Pktx9f_86Jp-k6ErAXsFh7yKrPafcdhEvoa_o`).

```bash
python3 -c "
import gspread
from google.oauth2.service_account import Credentials
creds = Credentials.from_service_account_file('automacoes/credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly','https://www.googleapis.com/auth/drive.readonly'])
client = gspread.authorize(creds)
ss = client.open_by_key('18IYDy4Pktx9f_86Jp-k6ErAXsFh7yKrPafcdhEvoa_o')
# Encontrar aba do mes e contar slots preenchidos por designer (20 = 100%, <20 = 0%)
import json
aba = next((a for a in ss.worksheets() if '{mes_nome}'.upper() in a.title.upper()), None)
if aba:
    dados = aba.get_all_values()
    print(json.dumps({'aba': aba.title, 'dados': dados[:25]}))
else:
    print(json.dumps({'erro': 'aba nao encontrada'}))
"
```

O agente analisa o output e determina para cada designer:
- Encontrar header com nomes (linha com 2+ nomes de designers)
- Contar linhas preenchidas (1 a 20) na coluna de cada designer
- 20/20 preenchidos = 100%, senao = 0%

**Aplica a:** Designers apenas

### Step 4: KPI — Novos Modelos de Video (via Google Sheets)

Mesma logica do Step 3, mas para editores.
Ler planilha de Videos (`10NyWM4CFJHyNFaveh48FGq7mfWrzOTWMwAH-rZEsJJY`).

- Encontrar header com nomes de editores
- Contar linhas preenchidas (1 a 20)
- >= 50% preenchidos (10/20) = 100%, senao = 0%

**Aplica a:** Editores apenas

### Step 5: KPI — Alteracoes por Responsabilidade (via Google Sheets)

**Ler 2 fontes e calcular:**

**5a. Refacoes** — planilha `1avv5PapqdKdPc92Uqxm-SW7LL6lcgJ3_D8Wz1461ieM`:
- Aba "refacoes"
- Filtrar por data (col 0) no mes/ano alvo
- Contar total de refacoes por pessoa (col 3 = nome)

**5b. Posts Criados** — planilha `1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I`:
- Aba do mes
- Designers: somar col Total (idx 5) por nome (col 1) das linhas semanais
- Editores: buscar totais individuais no resumo do lado direito

**5c. Calcular:**
```
alteracoes[membro] = 1 - (refacoes[membro] / posts_criados[membro])
```
Quanto maior, melhor (menos refacoes = mais qualidade).

**Aplica a:** Todos

### Step 6: Apresentar resultados (ELICIT)

Exibir TODOS os KPIs calculados:

```markdown
## 🎯 Metas Calculadas — {Mes} {Ano}

### Designers
| Nome | Alteracoes | Layout | Prazo |
|------|------------|--------|-------|
| Eloy | 85.3% ✅ | 100% ✅ | 85.7% ✅ |
| Humberto | 71.2% ⚠️ | 100% ✅ | 92.0% ✅ |
| ... | ... | ... | ... |

### Editores
| Nome | Alteracoes | Video | Prazo |
|------|------------|-------|-------|
| Ebertty | 78.1% ✅ | 100% ✅ | 88.3% ✅ |
| ... | ... | ... | ... |

📊 Prazo de Entrega calculado via ClickUp (dados reais)
📋 Demais KPIs lidos das planilhas-fonte
```

**OBRIGATORIO: Pedir confirmacao antes de gravar.**

```
Deseja gravar na planilha de Metas AV?
1. Sim, gravar e enviar DMs
2. Sim, sem DMs
3. Nao, cancelar
```

### Step 6.5: Auditoria COMPLETA (OBRIGATORIO — BLOQUEADOR)

**ANTES de gravar, executar `av-audit-metas` com TODOS os 4 KPIs.**

O auditor recalcula cada KPI a partir das planilhas-fonte:
- **Prazo de Entrega** → recalcula da planilha de Entregas (media das % semanais)
- **Layouts** → recalcula da planilha de Layouts (20/20 = 100%, senao 0%)
- **Videos** → recalcula da planilha de Videos (>=10/20 = 100%, senao 0%)
- **Alteracoes** → recalcula das planilhas de Refacoes + Posts Criados

Compara cada valor proposto com o recalculado. Se divergencia > 2% (numerico) ou diferente (binario) → **BLOQUEIO**.

**REGRA:** Todos os 4 KPIs devem passar ou NENHUM grava. Sem escrita parcial.

Somente se auditoria retornar APROVADO → seguir para Step 7.

### Step 7: Gravar na planilha de Metas

Escrever na planilha `1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc`.

```bash
python3 -c "
import gspread, json, sys
from google.oauth2.service_account import Credentials
creds = Credentials.from_service_account_file('automacoes/credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.readonly'])
client = gspread.authorize(creds)
ss = client.open_by_key('1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc')
# dados_json passado como argumento
dados = json.loads(sys.argv[1])
# encontrar aba, encontrar headers, escrever valores
# ... (agente monta o script com os valores calculados)
"
```

O agente monta o script Python com os valores calculados nos steps anteriores e executa.

**Estrutura da planilha de Metas:**
- 2 secoes: Designers (linhas 2-9) e Editores (linhas 13-16)
- Colunas: Nome Prestador | ... | Alteracoes por Responsabilidade | Novos Modelos | Prazo de Entrega
- Valores em formato decimal (0.85 = 85%)

### Step 8: Enviar DMs via ClickUp Chat

**Pular se `--skip-chat` ou se usuario escolheu opcao 2.**

Para cada colaborador (exceto Angelo), enviar DM com template:

```
{Saudacao}, {Nome}! 👋

Seguem suas **metas de {Mes} {Ano}** — Time Audiovisual Stark:

📊 **Seus KPIs do mes:**
• Alteracoes por Responsabilidade: **{alt}%** {✅|⚠️}
• {Novos Modelos de Layout|Video}: **{modelo}%** {✅|⚠️}
• Prazo de Entrega de Demandas: **{prazo}%** {✅|⚠️}

📝 **Nota Fiscal:** {Liberada|Pendente}

Qualquer duvida, me chama! 💬
```

**Enviar via ClickUp Chat MCP** (`clickup_send_chat_message`) ou via API REST.

**Channel IDs:**
| Colaborador | Channel ID |
|---|---|
| Angelo (relatorio) | 1393eg-26353 |
| Ebertty | 1393eg-61153 |
| Humberto | 1393eg-33113 |
| Eloy | 1393eg-61573 |
| Andre | 1393eg-26473 |
| Max | 1393eg-61713 |
| Karyne | 1393eg-61733 |
| Milena | 1393eg-61753 |
| Joao | 1393eg-61773 |
| Mateus | 1393eg-61793 |

**Rate limit:** 0.5s entre envios.

Apos todos os DMs, enviar **relatorio completo** para Angelo com:
- Resumo de todos os KPIs
- Contagem de DMs enviadas/falhas
- Destaques (melhor prazo, melhor alteracoes)

### Step 9: Reportar resultado

```markdown
## ✅ Metas Atualizadas — {Mes} {Ano}

- 📊 Prazo de Entrega: calculado via ClickUp MCP ({N} semanas, {N} consultas)
- 📋 Layouts/Videos/Alteracoes: lidos das planilhas-fonte
- 📝 Planilha: ✅ {N} colaboradores atualizados
- 📨 DMs ClickUp: ✅ {N} enviadas / ❌ {N} falhas

📊 [Abrir planilha](https://docs.google.com/spreadsheets/d/1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc/)
```

---

## Nota Fiscal — Criterios

Um colaborador tem NF **Liberada** se:
- Alteracoes por Responsabilidade >= 75%
- Prazo de Entrega >= 80%
- Novos Modelos (Layout ou Video) = 100%

Caso contrario: **Pendente**.

## Status das tarefas para classificacao (ClickUp)

| Classificacao | Status ClickUp |
|---|---|
| ENTREGUE | "edicao concluida", "concluido", "aguardando postagem", "aprovado", "arte aprovada", "finalizado" |
| EM ANDAMENTO | "edicao", "revisao" |
| NAO INICIADO | "a ser feito" |

## Veto Conditions

- **VETO** se ClickUp MCP indisponivel → "Nao foi possivel calcular Prazo de Entrega. Verifique a conexao MCP."
- **VETO** se `automacoes/credentials.json` nao existir → orientar setup
- **NUNCA** gravar sem confirmacao explicita do usuario
- **NUNCA** enviar DMs reais em modo simulacao
- **SE** ClickUp retornar 0 tarefas para o mes inteiro → alertar, possivelmente mes errado

## Completion Criteria

- [ ] Calculou janelas semanais do mes corretamente
- [ ] Consultou ClickUp MCP para CADA membro em CADA semana (prazo de entrega)
- [ ] Aplicou retry em erros temporarios (502, timeout)
- [ ] Leu KPIs de Layout/Video/Alteracoes das planilhas Google
- [ ] Apresentou TODOS os KPIs ao usuario antes de gravar
- [ ] Obteve confirmacao explicita
- [ ] Gravou valores na planilha de Metas AV
- [ ] Enviou DMs com template correto (se confirmado)
- [ ] Enviou relatorio para Angelo (ultimo, com contagem de DMs)
- [ ] Exibiu resumo final
