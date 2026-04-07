---
task: Diagnosticar Erro
responsavel: "@solucionador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Mensagem de erro (string ou exceção)
  - Contexto: agente de origem, cliente, task ClickUp (opcional)
Saida: |
  - Diagnóstico: categoria, severidade, strategy match
  - Decisão: auto-resolve ou escalar
Checklist:
  - "[ ] Receber erro e contexto"
  - "[ ] Classificar categoria e severidade"
  - "[ ] Buscar match em fallback-strategies.yaml"
  - "[ ] Decidir: auto-resolve ou escalar"
  - "[ ] Registrar diagnóstico no error-log.yaml"
---

# *diagnosticar

Classifica um erro recebido (severidade + categoria), busca fallback correspondente em `data/fallback-strategies.yaml` e decide se deve auto-resolver ou escalar para o gestor.

## Uso

```
*diagnosticar "Figma IMAGE fill timeout after 30s"
*diagnosticar "FileNotFoundError: /tmp/export.png" --agente designer-figma --cliente "Dra. Camila"
```

## Fluxo

1. **Receber erro** — Capturar mensagem de erro e contexto (agente origem, cliente, task)
2. **Classificar** — Determinar categoria e severidade:
   - Categorias: `figma`, `drive`, `clickup`, `sistema`, `imagem`
   - Severidades: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
3. **Match** — Buscar padrão correspondente em `data/fallback-strategies.yaml` usando regex do campo `pattern`
4. **Decidir** — Aplicar regras de auto-resolução:
   - Se `severity` in [LOW, MEDIUM] **E** fallback.type == "auto" **E** confidence >= 0.7 → **auto-resolve** (chamar `*fallback`)
   - Se `severity` in [HIGH, CRITICAL] **OU** fallback.type == "manual" **OU** confidence < 0.7 → **escalar** (chamar `*alertar`)
   - Se nenhum match encontrado → **escalar** como erro desconhecido
5. **Registrar** — Salvar diagnóstico no `data/error-log.yaml` via `*registrar-erro`

## Regras

- Máximo de 2 tentativas de match antes de classificar como "desconhecido"
- Nunca tentar auto-resolver erros HIGH ou CRITICAL
- Sempre registrar no log, mesmo erros auto-resolvidos
- Se o mesmo erro ocorrer 3+ vezes no mesmo dia: escalar independente de severidade

## Output

```yaml
diagnostico:
  erro: "mensagem original"
  categoria: figma
  severidade: LOW
  strategy_match: figma-image-fill-timeout
  fallback_disponivel: true
  decisao: auto-resolve  # ou escalar
  confianca: 0.95
  proxima_acao: "*fallback figma-image-fill-timeout"
```
