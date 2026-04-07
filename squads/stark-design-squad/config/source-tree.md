# Source Tree — Stark Design Squad

```
squads/stark-design-squad/
├── squad.yaml                              # Manifest principal
├── README.md                               # Documentação do squad
│
├── config/
│   ├── coding-standards.md                 # Convenções de nomenclatura e padrões
│   ├── tech-stack.md                       # Ferramentas e integrações
│   └── source-tree.md                      # Este arquivo
│
├── agents/                                 # 10 agentes
│   ├── orquestrador.md                     # Coordenador central
│   ├── designer-figma.md                   # Executor — layouts Figma
│   ├── web-designer-lp.md                  # Executor — LPs (Atomic Design)
│   ├── construtor-capa-reels.md            # Executor — capas Instagram
│   ├── qa-qualidade.md                     # Revisor — avaliação de entregas
│   ├── brand-guardian.md                   # Suporte — identidade visual
│   ├── pesquisador-ref.md                  # Suporte — referências visuais
│   ├── analytics-posts.md                  # Analista — métricas de desempenho
│   ├── monitor-refacoes.md                 # Analista — refações e planos de ação
│   └── solucionador.md                     # Suporte — detector/resolvedor de erros
│
├── tasks/                                  # 39 tasks (task-first architecture)
│   ├── delegar-tarefa.md                   # orquestrador
│   ├── consolidar-entrega.md               # orquestrador
│   ├── exportar-entrega.md                 # orquestrador (reusa figma-export-para-drive)
│   ├── alertar-atraso.md                   # orquestrador
│   ├── buscar-layout.md                    # orquestrador + designer-figma (Layout Index)
│   ├── registrar-feedback-layout.md        # orquestrador (Layout Index)
│   ├── criar-layout.md                     # designer-figma
│   ├── replicar-layout.md                  # designer-figma
│   ├── exportar-assets.md                  # designer-figma
│   ├── exportar-entrega-designer.md        # designer-figma (reusa figma-export-para-drive)
│   ├── indexar-layout.md                   # designer-figma (Layout Index)
│   ├── criar-lp.md                         # web-designer-lp
│   ├── replicar-lp.md                      # web-designer-lp
│   ├── criar-componente.md                 # web-designer-lp
│   ├── listar-atomos.md                    # web-designer-lp
│   ├── compor-organismo.md                 # web-designer-lp
│   ├── criar-capa.md                       # construtor-capa-reels
│   ├── criar-variacao-ab.md                # construtor-capa-reels
│   ├── avaliar-entrega.md                  # qa-qualidade
│   ├── gerar-laudo.md                      # qa-qualidade
│   ├── atualizar-ranking.md                # qa-qualidade
│   ├── consultar-marca.md                  # brand-guardian
│   ├── historico-fotos.md                  # brand-guardian
│   ├── registrar-uso.md                    # brand-guardian
│   ├── buscar-referencias.md               # pesquisador-ref (+Instagram via Apify)
│   ├── tendencias-nicho.md                 # pesquisador-ref
│   ├── gerar-moodboard.md                  # pesquisador-ref
│   ├── extrair-briefing-clickup.md         # pesquisador-ref (links, imagens, copy)
│   ├── desempenho-post.md                  # analytics-posts
│   ├── media-cliente.md                    # analytics-posts
│   ├── ranking-mensal.md                   # analytics-posts
│   ├── refacoes-semana.md                  # monitor-refacoes
│   ├── refacoes-por-cliente.md             # monitor-refacoes
│   ├── refacoes-por-designer.md            # monitor-refacoes
│   ├── plano-acao.md                       # monitor-refacoes
│   ├── diagnosticar-erro.md                # solucionador
│   ├── executar-fallback.md                # solucionador
│   ├── alertar-erro-clickup.md             # solucionador
│   └── registrar-erro.md                   # solucionador
│
├── workflows/
│   └── post-creation-flow.yaml             # Fluxo principal de criação de post
│
├── templates/
│   ├── laudo-qa-tmpl.md                    # Template de laudo QA
│   ├── plano-acao-tmpl.md                  # Template de plano de ação
│   └── alerta-erro-tmpl.md                 # Template de alerta de erro
│
├── data/
│   ├── brands/                             # YAMLs de brand por cliente
│   │   └── .gitkeep
│   ├── layouts/                            # Cache local do Layout Index
│   │   └── .gitkeep
│   ├── fallback-strategies.yaml            # Banco de fallbacks do Solucionador
│   └── error-log.yaml                      # Histórico de erros
│
├── checklists/
│   └── .gitkeep
├── tools/
│   └── .gitkeep
└── scripts/
    └── .gitkeep
```

## Dependências Externas

| Arquivo | Localização | Usado por |
|---------|-------------|-----------|
| `automacoes/upload_drive.py` | Raiz do projeto | orquestrador, designer-figma |
| `automacoes/credentials.json` | Raiz do projeto | Google Drive API |
| `.claude/commands/figma-export-para-drive.md` | Raiz do projeto | orquestrador, designer-figma |

## Blueprint

O blueprint de design deste squad está em:
```
squads/.designs/stark-design-squad-design.yaml
```
