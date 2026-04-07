---
task: AV Audit Metas
agent: av-monitor
version: 2.0.0
elicit: false
mode: automated
---

# Task: av-audit-metas

Auditor de dados que valida TODOS os KPIs antes de gravar na planilha de Metas. Recalcula cada KPI a partir das planilhas-fonte e bloqueia escrita se houver divergencia.

**Principio:** Nenhum valor entra na planilha de Metas sem passar por auditoria.

## Quando executar

- **OBRIGATORIO** antes de qualquer escrita na planilha de Metas
- Chamado automaticamente pelo `av-metas` no Step 6.5
- Pode ser chamado manualmente: `*audit-metas Março`

## Inputs

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| `mes` | string | Sim | Nome do mes (ex: "Março") |
| `valores_propostos` | dict | Sim | {nome: {prazo, layout, video, alteracoes}} |

## Planilhas-fonte (leitura)

| KPI | Planilha | ID |
|-----|----------|----|
| Prazo de Entrega | Entregas Semanal | `1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA` |
| Novos Modelos Layout | Layouts Mensais | `18IYDy4Pktx9f_86Jp-k6ErAXsFh7yKrPafcdhEvoa_o` |
| Novos Modelos Video | Videos Mensais | `10NyWM4CFJHyNFaveh48FGq7mfWrzOTWMwAH-rZEsJJY` |
| Alteracoes (refacoes) | Refacoes | `1avv5PapqdKdPc92Uqxm-SW7LL6lcgJ3_D8Wz1461ieM` |
| Alteracoes (posts) | Analise de Artes | `1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I` |

## Planilha destino (escrita bloqueada ate aprovacao)

| Planilha | ID |
|----------|----|
| Metas AV | `1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc` |

## Metas para "BATEU"

| KPI | Threshold | Aplica a |
|-----|-----------|----------|
| Prazo de Entrega | >= 80% | Todos |
| Novos Modelos Layout | = 100% | Designers |
| Novos Modelos Video | = 100% | Editores |
| Alteracoes por Responsabilidade | >= 75% | Todos |

---

## Steps

### Step 1: Auditar Prazo de Entrega

**Fonte:** Planilha de Entregas, aba do mes.

**Recalculo:**
```
Para cada membro:
  Ler todas as semanas (S1, S2, ..., SN)
  pct_semana = Posts Entregues / Posts a Serem Entregues
  prazo_recalculado = media(pct_semana_1, ..., pct_semana_N)
```

**REGRAS:**
- E a MEDIA DAS PORCENTAGENS semanais, NAO soma(entregues)/soma(total)
- Ignorar linhas com data fora do mes (ex: "05/01" em aba de Marco)
- Ignorar Semana 5 se nao tiver dados preenchidos
- Ignorar Angelo (nao entra na meta)

**Comparacao:**
```
diff = abs(valor_proposto - prazo_recalculado)
```

### Step 2: Auditar Novos Modelos de Layout

**Fonte:** Planilha de Layouts, aba do mes.
**Aplica a:** Designers apenas.

**Recalculo:**
```
Para cada designer:
  Encontrar coluna com nome do designer no header
  Contar linhas preenchidas (celulas nao vazias) abaixo do header
  Se contagem >= 20 → layout_recalculado = 1.0 (100%)
  Senao → layout_recalculado = 0.0 (0%)
```

**Comparacao:** Binario — recalculado DEVE ser igual ao proposto.

### Step 3: Auditar Novos Modelos de Video

**Fonte:** Planilha de Videos, aba do mes.
**Aplica a:** Editores apenas.

**Recalculo:**
```
Para cada editor:
  Encontrar coluna com nome do editor no header
  Contar linhas preenchidas abaixo do header
  Se contagem >= 10 (50% de 20) → video_recalculado = 1.0 (100%)
  Senao → video_recalculado = 0.0 (0%)
```

**Comparacao:** Binario — recalculado DEVE ser igual ao proposto.

### Step 4: Auditar Alteracoes por Responsabilidade

**Fontes:**
- Refacoes: planilha `1avv5...`, aba "refacoes"
- Posts criados: planilha `1fmO...`, aba do mes

**Recalculo:**
```
Para cada membro:
  refacoes = contagem de linhas onde col_data esta no mes E col_nome = membro
  posts = total de posts criados pelo membro no mes
  alteracoes_recalculado = 1 - (refacoes / posts)
  Se posts == 0 → alteracoes_recalculado = 1.0 (sem posts = sem refacoes)
```

**Comparacao:**
```
diff = abs(valor_proposto - alteracoes_recalculado)
```

### Step 5: Classificar cada valor

| Diferenca | Tipo KPI | Classificacao | Acao |
|-----------|----------|---------------|------|
| <= 0.5% | Numerico (Prazo, Alteracoes) | OK | Permitir |
| 0.5% a 2% | Numerico | AVISO | Permitir com log |
| > 2% | Numerico | BLOQUEIO | Impedir escrita |
| Igual | Binario (Layout, Video) | OK | Permitir |
| Diferente | Binario | BLOQUEIO | Impedir escrita |

### Step 6: Emitir relatorio completo

```markdown
## Auditoria de Metas — {Mes} {Ano}

### KPI 1: Prazo de Entrega (meta >= 80%)
| Membro | Entregas | Proposto | Diff | Status |
|--------|----------|----------|------|--------|
| Eloy | 82.50% | 82.50% | 0.00% | OK |
| ... | ... | ... | ... | ... |

### KPI 2: Novos Modelos de Layout (meta = 100%)
| Designer | Recalc | Proposto | Status |
|----------|--------|----------|--------|
| Eloy | 100% | 100% | OK |
| ... | ... | ... | ... |

### KPI 3: Novos Modelos de Video (meta = 100%)
| Editor | Recalc | Proposto | Status |
|--------|--------|----------|--------|
| Ebertty | 100% | 100% | OK |
| ... | ... | ... | ... |

### KPI 4: Alteracoes por Responsabilidade (meta >= 75%)
| Membro | Refacoes | Posts | Recalc | Proposto | Diff | Status |
|--------|----------|-------|--------|----------|------|--------|
| Eloy | 3 | 50 | 94% | 94% | 0% | OK |
| ... | ... | ... | ... | ... | ... | ... |

---

### Resultado Final: {APROVADO | BLOQUEADO}

**Resumo:**
- Total de verificacoes: N
- OK: N
- Avisos: N (listar)
- Bloqueios: N (listar)

**Decisao:** {Liberado para escrita | Escrita BLOQUEADA — corrigir divergencias}
```

### Step 7: Decisao final

- **APROVADO**: Zero bloqueios → liberar escrita na Metas
- **BLOQUEADO**: 1+ bloqueio → impedir escrita, listar TODAS as divergencias
  - Exibir valor recalculado vs proposto
  - Indicar qual planilha-fonte foi consultada
  - Sugerir: "Use o valor recalculado ou verifique a planilha-fonte"

## Veto Conditions

- **VETO** se qualquer planilha-fonte nao tem aba do mes
- **VETO** se membro do time nao encontrado na planilha-fonte
- **VETO** se divergencia > 2% em KPI numerico
- **VETO** se divergencia em KPI binario (100% vs 0%)
- **NUNCA** permitir escrita parcial (todos KPIs devem passar ou nenhum grava)

## Completion Criteria

- [ ] Leu e recalculou Prazo de Entrega da planilha de Entregas
- [ ] Leu e recalculou Layouts da planilha de Layouts
- [ ] Leu e recalculou Videos da planilha de Videos
- [ ] Leu e recalculou Alteracoes das planilhas de Refacoes + Posts
- [ ] Comparou TODOS os valores propostos com recalculados
- [ ] Classificou cada comparacao (OK / AVISO / BLOQUEIO)
- [ ] Emitiu relatorio completo com os 4 KPIs
- [ ] Decisao final: APROVADO ou BLOQUEADO
