# Stark Design Squad

Squad de agentes de IA especializados em produção, revisão e entrega de conteúdo visual para clientes de marketing digital da Stark Mkt.

## Composição

| Agente | Tipo | Responsabilidade |
|--------|------|-----------------|
| **Orquestrador** | Coordinator | Interface com o gestor, distribuição de tarefas, consolidação de entregas |
| **Designer Figma** | Executor | Criar e replicar layouts no Figma seguindo identidade visual |
| **Web Designer LP** | Executor | Construir landing pages com sistema Atomic Design |
| **Construtor Capa Reels** | Executor | Criar capas de reels otimizadas para performance no Instagram |
| **QA de Qualidade** | Reviewer | Avaliar entregas com 5 critérios ponderados (nota 0-10) |
| **Brand Guardian** | Support | Manter identidade visual e histórico de fotos por cliente |
| **Pesquisador Ref** | Support | Buscar referências visuais e tendências por nicho |
| **Analytics Posts** | Analyst | Monitorar desempenho de posts e tripla validação |
| **Monitor Refações** | Analyst | Rastrear refações, identificar padrões e gerar planos de ação |
| **Solucionador** | Support | Detectar erros, executar fallbacks automáticos, alertar gestor via ClickUp Chat |

## Fluxo Principal

```
Gestor → Orquestrador → Brand Guardian (guidelines)
                      → Layout Index (*buscar-layout — trabalhos anteriores)
                      → Pesquisador Ref (referências)
                      → Agente Executor (design)
                      → QA de Qualidade (avaliação)
                      → Exportar (Drive + ClickUp)
                      → Indexar Layout (*indexar-layout — banco de layouts)
                      → Monitor Refações (se houve refação)
                      → Analytics (métricas pós-publicação)

Fluxo de Feedback:
  Feedback externo → *registrar-feedback → Layout Index atualizado

Fluxo de Erro (qualquer etapa):
  Erro detectado → Solucionador (*diagnosticar)
                 → LOW/MEDIUM + auto → *fallback → continua fluxo
                 → HIGH/CRITICAL    → *alertar  → gestor decide
```

## Integrações

- **Figma** — Design, componentes, exportação (MCP)
- **ClickUp** — Tasks, subtasks, status, prazos, chat (MCP)
- **Google Drive** — Armazenamento por cliente (Script)
- **Google Sheets** — Métricas, ranking, refações, Layout Index (Script)
- **Web Search** — Referências visuais (Nativo)

## Skills Externas

```bash
npx skills add nextlevelbuilder/ui-ux-pro-max-skill@ui-ux-pro-max
npx skills add anthropics/skills@frontend-design
npx skills add giuseppe-trisciuoglio/developer-kit@shadcn-ui
npx skills add supercent-io/skills-template@web-accessibility
npx skills add vercel-labs/agent-skills@web-design-guidelines
```

## Setup

1. Instalar dependências Python: `pip install google-api-python-client google-auth`
2. Configurar `automacoes/credentials.json` (service account Google)
3. Compartilhar pasta "Clientes" do Drive com o service account
4. Instalar skills externas (comandos acima)
5. Verificar acesso ao Figma e ClickUp via MCP

## Layout Index

Banco de layouts pesquisavel no Google Sheets. Uma aba por cliente, cada linha = 1 layout entregue.

| Comando | Agente | Funcao |
|---------|--------|--------|
| `*buscar-layout` | Orquestrador, Designer Figma | Busca layouts por cliente/tipo/tags/nota |
| `*indexar-layout` | Designer Figma | Registra layout entregue no indice |
| `*registrar-feedback` | Orquestrador | Registra feedback externo (cliente/copy/gestor) |

**Colunas**: ID, Tipo, Subtipo, Data, Designer, Figma URL, Node ID, Drive Path, Formato, Nota QA, Veredito, Refacoes, Tempo, Feedback, Fonte, Tags, Engajamento, Observacoes.

## Estrutura

```
squads/stark-design-squad/
├── squad.yaml          # Manifest
├── agents/             # 10 agentes
├── tasks/              # 38 tasks
├── workflows/          # Fluxo de criacao de post
├── templates/          # Laudo QA, Plano de Acao
├── config/             # Standards, tech stack, source tree
├── data/brands/        # Brand guidelines por cliente (YAML)
├── data/layouts/       # Cache local do Layout Index
└── README.md           # Este arquivo
```

## Blueprint

Design completo: `squads/.designs/stark-design-squad-design.yaml`

---

*Stark Mkt - Design Squad v1.0.0*
*Criado por @squad-creator (Craft) em 2026-03-26*
