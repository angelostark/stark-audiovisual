---
name: preencher-entrega-posts
description: >
  Calcula a % de entrega de posts no prazo (até quarta 20h) para cada
  designer/editor do time Audiovisual da Stark. Lê dados do Google Sheets
  (alimentado semanalmente pelo Make.com).

  Use SEMPRE que o usuário pedir: "preencher entrega de posts", "verificar entregas",
  "calcular entregas da semana", "meta de entrega", "prazo de entrega posts",
  "rodar entrega posts", ou qualquer variação de verificar/calcular/preencher
  entregas de posts do time audiovisual.
---

# Preencher Entrega de Posts — Stark Audiovisual

Essa skill calcula o percentual de entregas no prazo (quarta 20h) por designer/editor,
lendo dados brutos de uma planilha Google Sheets alimentada automaticamente pelo Make.com
toda quarta-feira às 20h.

---

## Arquitetura

```
Make.com (Quarta 20h) → ClickUp API → Google Sheets "Dados Entregas AV - Raw"
Skill (sob demanda)   → Lê Sheets → Calcula % → Exibe + Atualiza planilha de entregas
```

---

## Constantes

### Planilhas

| Planilha | ID | Uso |
|----------|----|-----|
| Dados Brutos (Make.com) | `1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA` | Fonte de dados — aba "Dados Brutos" (mesma planilha) |
| Entregas (destino) | `1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA` | Resultado — aba do mês |

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

### ETAPA ÚNICA — Executar script Python

Execute o script diretamente via Bash:

```bash
python3 /Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/preencher_entregas_clickup.py
```

**Argumentos opcionais:**

| Argumento | Uso | Exemplo |
|-----------|-----|---------|
| `--semana` | Semana específica (se diferente da atual) | `--semana "16/03 a 22/03"` |
| `--quarta` | Data da quarta de referência | `--quarta 2026-03-18` |
| `--mes` | Aba do mês na planilha de entregas | `--mes Março` |
| `--dry-run` | Apenas calcula, sem escrever na planilha | `--dry-run` |

**Exemplo completo:**
```bash
python3 /Users/angelogabriel/Documents/AIOS-CRIADOR/automacoes/preencher_entregas_clickup.py --dry-run
```

O script faz tudo automaticamente:
1. Lê aba "Dados Brutos" da planilha alimentada pelo Make.com
2. Filtra tarefas da semana atual
3. Calcula demandas e entregas no prazo por colaborador
4. Exibe tabela com resultados
5. Atualiza planilha de entregas (se não --dry-run)

---

## Erros comuns e como lidar

| Situação | Ação |
|----------|------|
| Planilha de dados brutos vazia | Make.com pode não ter rodado — verificar cenário no Make.com |
| Semana não encontrada nos dados | Confirmar que a semana buscada corresponde ao formato do Make.com |
| Erro de autenticação Google | Verificar `credentials.json` em `automacoes/` |
| Nenhuma tarefa para algum colaborador | Normal se a pessoa não teve demandas na semana |
| Dados desatualizados | Verificar se Make.com rodou na quarta — checar aba "Status" |

---

## Dependências

| Componente | Tipo | Detalhes |
|------------|------|---------|
| Google Sheets API | API | Lê dados brutos + escreve entregas |
| Python 3 + gspread | Runtime | Script de processamento |
| Make.com | Automação | Alimenta planilha toda quarta 20h |
| credentials.json | Auth | Service account Google (`automacoes/credentials.json`) |

---

## Status de integração

| Serviço | Status | Via |
|---------|--------|-----|
| ClickUp | Indireto | Make.com coleta → Google Sheets |
| Google Sheets | Automático | Script lê e escreve via API |
| Make.com | Automático | Roda quarta 20h, grava dados brutos |
| Notificação falha | Automático | LaunchAgent checa quinta 9h |
