# Tech Stack — Stark Design Squad

## Ferramentas de Design
| Ferramenta | Uso | Acesso |
|-----------|-----|--------|
| Figma | Design de interfaces, peças e LPs | MCP (get_metadata, get_screenshot) |
| Figma Make | Geração de ideias de distribuição mobile | Manual |

## Gestão e Comunicação
| Ferramenta | Uso | Acesso |
|-----------|-----|--------|
| ClickUp | Tasks, subtasks, status, prazos | MCP (search, get_task, update_task, create_task_comment) |
| ClickUp Chat | Mensagens no chat de subtarefas, @menções | MCP (send_chat_message) |

## Armazenamento
| Ferramenta | Uso | Acesso |
|-----------|-----|--------|
| Google Drive | Armazenamento de entregas por cliente | Script (upload_drive.py) |
| Google Sheets | Métricas, ranking, refações | Script (google-api-python-client) |

## Processamento de Imagem
| Ferramenta | Uso | Acesso |
|-----------|-----|--------|
| Pillow (PIL) | Composição de fotos em layouts (fluxo padrão para posts com imagens) | Python (pip install Pillow) |

## Scripts e Automações
| Script | Função | Linguagem |
|--------|--------|-----------|
| `automacoes/upload_drive.py` | Upload automático para Drive | Python |
| `.claude/commands/figma-export-para-drive.md` | Fluxo completo Figma → Drive → ClickUp | Skill Claude |

## Skills Externas
| Skill | Agentes | Instalação |
|-------|---------|------------|
| UI-UX-Pro-Max | Designer, Web Designer LP, QA | `npx skills add nextlevelbuilder/ui-ux-pro-max-skill@ui-ux-pro-max` |
| frontend-design | Web Designer LP, Capa Reels | `npx skills add anthropics/skills@frontend-design` |
| shadcn-ui | Web Designer LP | `npx skills add giuseppe-trisciuoglio/developer-kit@shadcn-ui` |
| web-accessibility | Web Designer LP, QA | `npx skills add supercent-io/skills-template@web-accessibility` |
| web-design-guidelines | Web Designer LP, Designer, Capa Reels | `npx skills add vercel-labs/agent-skills@web-design-guidelines` |

## Dependências Python
```
google-api-python-client
google-auth
Pillow
```

## Dados Locais
| Tipo | Path | Formato |
|------|------|---------|
| Brand guidelines por cliente | `data/brands/[cliente].yaml` | YAML |
| Fallback strategies | `data/fallback-strategies.yaml` | YAML |
| Error log | `data/error-log.yaml` | YAML |
