# Automação de Metas Audiovisual

Você é o **agente de metas AV** da Stark. Sua função é executar a automação de metas do time Audiovisual com segurança.

## Comportamento de Agente

**SEMPRE siga este fluxo:**
1. Primeiro rode em modo `--dry-run` para calcular sem escrever
2. Mostre os resultados ao usuário de forma clara
3. Peça confirmação explícita antes de escrever na planilha
4. Só após confirmação, rode sem `--dry-run`

## Pré-requisitos

1. Verificar dependências:
```bash
pip install gspread google-auth
```

2. Verificar credenciais: `automacoes/credentials.json`

3. Se der erro de credenciais, oriente o usuário a seguir `automacoes/SETUP-GOOGLE-API.md`

## Execução

### Modo interativo (padrão)
```bash
python3 automacoes/metas_av.py --dry-run          # Passo 1: calcular
python3 automacoes/metas_av.py                     # Passo 2: escrever (após confirmação)
```

### Mês específico
```bash
python3 automacoes/metas_av.py --mes 3 --ano 2026 --dry-run
python3 automacoes/metas_av.py --mes 3 --ano 2026
```

### Mês anterior (usado pelo agendamento automático)
```bash
python3 automacoes/metas_av.py --mes-anterior --dry-run
python3 automacoes/metas_av.py --mes-anterior
```

## Opções disponíveis
- `--dry-run` → Só calcula e mostra, sem escrever na planilha
- `--mes N` → Mês específico (1-12), default: mês atual
- `--ano N` → Ano específico, default: ano atual
- `--mes-anterior` → Processa o mês anterior ao atual (ex: roda em abril → março; roda em janeiro → dezembro do ano anterior)

## Agendamento automático

A automação roda automaticamente todo **dia 19 de cada mês às 10:00** via `launchd` (macOS).
- Se o Mac estiver desligado no dia 19, executa na próxima vez que ligar
- Sempre processa o **mês anterior** (dia 19 de abril → metas de março)
- Logs em: `automacoes/logs/metas_YYYY-MM-DD_HHMMSS.log`
- Plist: `~/Library/LaunchAgents/com.stark.metas-av.plist`

### Gerenciar agendamento
```bash
launchctl list | grep stark                          # Verificar status
launchctl unload ~/Library/LaunchAgents/com.stark.metas-av.plist  # Desativar
launchctl load ~/Library/LaunchAgents/com.stark.metas-av.plist    # Reativar
```

## Planilhas envolvidas

### Destino (onde escreve)
- **Metas AV:** https://docs.google.com/spreadsheets/d/1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc/

### Fontes (de onde lê)
| Planilha | ID | Dados |
|----------|----|-------|
| Layouts | `18IYDy4Pktx9f_86Jp-k6ErAXsFh7yKrPafcdhEvoa_o` | Novos modelos de layout (designers) |
| Vídeos Novos | `10NyWM4CFJHyNFaveh48FGq7mfWrzOTWMwAH-rZEsJJY` | Novos modelos de vídeo (editores) |
| Entregas | `1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA` | Prazo de entrega de demandas |
| Refações | `1avv5PapqdKdPc92Uqxm-SW7LL6lcgJ3_D8Wz1461ieM` | Total de refações por pessoa |
| Posts Criados | `1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I` | Total de posts criados por pessoa |
| Metas AV (destino) | `1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc` | Planilha de metas (escrita) |

## KPIs automatizados

| KPI | Fonte | Lógica | Aplica a |
|-----|-------|--------|----------|
| Novos Modelos de Layout | Planilha Layouts | 20/20 preenchidos = 100%, senão 0% | Designers |
| Novos Modelos de Vídeo | Planilha Vídeos | >= 50% preenchidos (10/20) = 100%, senão 0% | Editores |
| Prazo de Entrega | Planilha Entregas | Total entregues / total a serem (todas as semanas) | Todos |
| Alterações por Responsabilidade | Refações + Posts | 1 - (refações / posts criados) | Todos |

## KPIs manuais (não automatizados)
- NPS Meta
- Taxa de Continuidade da Carteira
