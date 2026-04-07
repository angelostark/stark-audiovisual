---
task: Executar Fallback
responsavel: "@solucionador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - ID da strategy em fallback-strategies.yaml
  - Contexto original do erro (agente, cliente, task)
Saida: |
  - Resultado da execução do fallback (success | partial | failed)
  - Se failed: escalar para gestor
Checklist:
  - "[ ] Carregar strategy do fallback-strategies.yaml"
  - "[ ] Validar que é auto-resolvível"
  - "[ ] Executar steps da strategy em ordem"
  - "[ ] Verificar resultado"
  - "[ ] Registrar resultado no error-log.yaml"
---

# *fallback

Executa uma estratégia de fallback conhecida a partir do banco `data/fallback-strategies.yaml`.

## Uso

```
*fallback figma-image-fill-timeout
*fallback drive-pasta-nao-existe --cliente "Dra. Camila"
*fallback clickup-rate-limit --retry 2
```

## Fluxo

1. **Carregar strategy** — Ler `data/fallback-strategies.yaml` e encontrar strategy pelo ID
2. **Validar** — Confirmar que:
   - Strategy existe
   - `fallback.type` == "auto"
   - `confidence` >= 0.7
   - Número de retries não excedeu `max_retries` (se definido)
3. **Executar** — Seguir `fallback.steps` em ordem sequencial
4. **Verificar** — Checar se a operação original agora funciona
5. **Resultado**:
   - `success` → Operação completada, continuar fluxo normal
   - `partial` → Operação parcial, alertar gestor com contexto
   - `failed` → Fallback não resolveu, escalar via `*alertar`
6. **Registrar** — Atualizar `data/error-log.yaml` com resultado via `*registrar-erro`

## Strategies Auto-Resolvíveis

| Strategy ID | Ação |
|-------------|------|
| `figma-image-fill-timeout` | Pillow compositing (fluxo padrão) |
| `figma-mcp-timeout` | Retry com backoff (5s, 15s, 45s) |
| `drive-pasta-nao-existe` | Criar pasta e retentar |
| `clickup-rate-limit` | Retry com backoff (30s, 60s) |
| `clickup-task-nao-encontrada` | Buscar por nome |
| `path-nao-existe` | mkdir -p e retentar |

## Regras

- Nunca executar fallback manual (type != "auto") sem aprovação do gestor
- Respeitar `max_retries` da strategy — nunca exceder
- Se fallback falhar: NÃO tentar novamente, escalar imediatamente
- Tempo máximo por fallback: 120 segundos — após isso, considerar `failed`
- Sempre passar contexto original (cliente, task, agente) para o log
