# 🎬 Audiovisual Squad — Stark

Squad para liderança e monitoramento da área Audiovisual da Stark.

## Agentes

| Agente | Função |
|--------|--------|
| `av-monitor` | Monitor de entregas — analisa ClickUp em tempo real |

## Slash Commands (use diretamente no Claude Code)

| Comando | O que faz |
|---------|-----------|
| `/av-status` | Status geral da semana — todos os clientes e membros |
| `/av-atrasados` | Lista tudo que está atrasado ou em risco |
| `/av-membro Eloy` | Scorecard individual de um membro da equipe |
| `/av-cliente Cadu` | Status de produção de um cliente específico |
| `/av-relatorio` | Relatório completo + PDF via Gamma |

## Uso do Agente

```
@av-monitor

*status-semanal       # Status geral
*atrasados            # O que está atrasado
*por-membro Eloy      # Scorecard do Eloy
*por-cliente Cadu     # Status do Dr. Cadu
*gerar-relatorio      # Relatório PDF completo
```

## Workflow Semanal

Execute toda segunda-feira:
```
@aiox-master *workflow av-weekly-review
```

Isso executa automaticamente:
1. Status geral de todas as entregas
2. Lista de atrasados
3. Scorecard de cada membro (designers + editores)
4. Status dos clientes em risco
5. Geração do relatório PDF via Gamma

## Fonte de Dados

- **ClickUp:** Lista "Agenda de Postagem 3.0"
  - Space: Agência [Operacional]
  - Folder: Comunicação
  - List ID: `901324888130`
- **Exportação:** Gamma MCP (PDF/apresentação)

## Equipe Configurada

**Designers:** Eloy Lopes, Humberto Sales, Max Ayalla, Milena Araújo, Mateus Deckmann

**Editores:** Ebertty Matnai, João Andare, André Araújo

**Estrategistas:** Matheus Peleteiro, Bruna Santana, Thaynara Castro, Evany Bandeira, Daniela Cabral, Germana Souza, Gabriella Andrade

## Estrutura

```
audiovisual-squad/
├── squad.yaml                         # Manifest do squad
├── agents/
│   └── av-monitor.md                  # Agente principal
├── tasks/
│   ├── av-status-semanal.md           # Task: status geral
│   ├── av-atrasados.md                # Task: atrasados
│   ├── av-por-membro.md               # Task: por membro
│   ├── av-por-cliente.md              # Task: por cliente
│   └── av-gerar-relatorio.md          # Task: relatório PDF
├── workflows/
│   └── av-weekly-review.yaml          # Workflow semanal
├── checklists/
│   └── av-monitor-quality-gate.md     # Checklist de qualidade
├── templates/
│   └── relatorio-av-tmpl.md           # Template do relatório
└── data/
    └── av-team-config.yaml            # Config do time + IDs ClickUp
```

---
*Audiovisual Squad v1.0 — Stark | Criado em: 2026-03-24*
