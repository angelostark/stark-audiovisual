---
task: Registrar Erro
responsavel: "@solucionador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Diagnóstico completo do erro
  - Resultado da resolução (success, partial, failed, escalated)
  - Contexto: agente, cliente, task
Saida: |
  - Entrada adicionada em data/error-log.yaml
  - Padrões recorrentes identificados (se houver)
Checklist:
  - "[ ] Gerar ID sequencial para o erro"
  - "[ ] Montar entrada com todos os campos"
  - "[ ] Adicionar ao error-log.yaml"
  - "[ ] Verificar padrões recorrentes"
---

# *registrar-erro

Registra um erro no histórico `data/error-log.yaml` e identifica padrões recorrentes.

## Uso

Chamado internamente por `*diagnosticar`, `*fallback` e `*alertar`. Raramente usado diretamente.

```
*registrar-erro --categoria figma --severidade LOW --mensagem "timeout" --resultado success
```

## Fluxo

1. **Gerar ID** — Formato: `ERR-{NNN}` sequencial baseado no último ID do log
2. **Montar entrada** — Preencher todos os campos:
   ```yaml
   - id: "ERR-001"
     timestamp: "2026-03-27T14:30:00-03:00"
     category: figma
     severity: LOW
     error_message: "mensagem original"
     strategy_used: figma-image-fill-timeout
     action_taken: pillow-compositing
     auto_resolved: true
     result: success
     context:
       cliente: "Dr. George"
       task_clickup: "abc123"
       agente_origem: designer-figma
     notes: "Detalhes adicionais"
   ```
3. **Adicionar** — Append na lista `entries` do `data/error-log.yaml`
4. **Analisar padrões** — Verificar:
   - Mesmo erro 3+ vezes no mesmo dia → alertar padrão recorrente
   - Mesmo agente com 5+ erros na semana → sugerir revisão
   - Mesma categoria com 10+ erros no mês → sugerir ação preventiva

## Regras

- Sempre usar timezone America/Bahia (UTC-3) no timestamp
- Nunca sobrescrever entradas existentes
- Manter log limpo: máximo 500 entradas (FIFO se exceder)
- Campos obrigatórios: id, timestamp, category, severity, error_message, result

## Comando *erros

O comando `*erros` é um alias de leitura que mostra o histórico:

```
*erros                      # Últimos 10 erros
*erros --categoria figma    # Filtrar por categoria
*erros --dia 2026-03-27     # Filtrar por dia
*erros --padroes            # Mostrar padrões recorrentes
```

### Output de *erros

```
📋 Histórico de Erros — Design Squad

Total: 15 erros | Auto-resolvidos: 10 (67%) | Escalados: 5 (33%)

Últimos 10:
| # | Data | Categoria | Severidade | Resultado |
|---|------|-----------|------------|-----------|
| ERR-015 | 27/03 14:30 | figma | LOW | ✅ auto |
| ERR-014 | 27/03 11:00 | clickup | LOW | ✅ auto |
| ERR-013 | 26/03 16:45 | drive | HIGH | 🚨 escalado |

Padrões detectados:
- ⚠️ "figma-mcp-timeout" ocorreu 4x esta semana
```
