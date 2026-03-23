---
name: Preencher Entrega de Posts
description: Processa JSONs do ClickUp contabilizando demandas vs entregues (regra Quarta 20:00) e popula a Planilha de Entregas.
---

# Skill: Preencher Entrega de Posts (ClickUp → Sheets)

## O que a skill faz?
Ao executar esta automação, os arquivos gerados contendo os dados brutos de tarefas do ClickUp (`/tmp/clickup_raw_*.json`) são processados para gerar as métricas de entrega semanais.
1. Carrega todas as tarefas alocadas aos designers/editores.
2. Compara a data de última atualização de um status concluído (ex. "edição concluída") com a **Quarta-feira às 20h daquela respectiva semana**.
3. Atualiza, diretamente no Google Sheets (Planilha de Entregas), as colunas **Posts a Serem** e **Posts Entregues** e já re-calcula as porcentagens na semana vigente.

## Como Executar
Sempre que o Claude (ou você mesmo via Script) puxar os JSONs para o `/tmp/`, chame o script principal listando as variáveis para encontrar o registro correto na planilha.

```bash
python3 automacoes/preencher_entregas_clickup.py --quarta "2026-03-18" --semana "16/03 a 22/03" --mes "Março"
```

### Argumentos
- `--quarta`: A data (YYYY-MM-DD) correspondente à **Quarta-feira limite** da semana de análise. Usado para o corte de prazo "Entregue" (às 20:00).
- `--semana`: Como a semana está descrita na célula de data na Planilha de Entregas, ex: `"16/03 a 22/03"`.
- `--mes`: A aba do mês na planilha, ex `"Março"`.
- `--dry-run`: (Opcional) Apenas calcula e exibe no terminal a soma dos resultados sem atualizar o Google Sheets (modo seguro).

## Exemplo Completo de Extração + Processamento
Se caso necessitar abstrair toda a regra de baixar os JSONs, você pode ordenar um Parallel Agent via AIOX para carregar as tarefas do ClickUp na sua `/tmp` antes de rodar o script python.
