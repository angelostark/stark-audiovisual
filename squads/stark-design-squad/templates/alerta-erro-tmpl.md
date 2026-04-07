# Template: Alerta de Erro — Solucionador

## Formato

```
{emoji} ALERTA — Solucionador Design Squad

Severidade: {severidade}
Categoria: {categoria}
Erro: {mensagem_erro}

Contexto:
- Cliente: {cliente}
- Agente: {agente_origem}
- Task: {task_clickup_id}

{secao_fallback}

{mencao}
```

## Variáveis

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{emoji}` | Emoji por severidade (ver tabela) | 🚨 |
| `{severidade}` | LOW, MEDIUM, HIGH, CRITICAL | HIGH |
| `{categoria}` | figma, drive, clickup, sistema, imagem | figma |
| `{mensagem_erro}` | Mensagem original do erro | "Figma file not found" |
| `{cliente}` | Nome do cliente (ou "N/A") | "Dra. Camila" |
| `{agente_origem}` | Agente que gerou o erro | designer-figma |
| `{task_clickup_id}` | ID da task no ClickUp (ou "N/A") | "abc123" |
| `{secao_fallback}` | Texto sobre fallback (ver abaixo) | |
| `{mencao}` | @menção se HIGH/CRITICAL | "@Angelo — ação necessária" |

## Emoji por Severidade

| Severidade | Emoji |
|-----------|-------|
| LOW | ℹ️ |
| MEDIUM | ⚠️ |
| HIGH | 🚨 |
| CRITICAL | 🔴 |

## Seção Fallback

### Se fallback foi tentado e falhou:
```
Fallback tentado: {strategy_id}
Resultado: FALHOU — {motivo}
Ação necessária: {acao_manual}
```

### Se não há fallback disponível:
```
Sem fallback automático disponível.
Ação necessária: {acao_manual}
```

### Se fallback resolveu parcialmente:
```
Fallback parcial: {strategy_id}
Resultado: {descricao_parcial}
Ação necessária: Verificar resultado e completar manualmente
```

## Exemplos

### Erro HIGH — Figma inacessível
```
🚨 ALERTA — Solucionador Design Squad

Severidade: HIGH
Categoria: figma
Erro: "File not found: abc123xyz"

Contexto:
- Cliente: Dr. George
- Agente: designer-figma
- Task: 86abc123

Sem fallback automático disponível.
Ação necessária: Fornecer link correto do arquivo Figma

@Angelo — ação necessária
```

### Erro LOW — Rate limit ClickUp (informativo)
```
ℹ️ ALERTA — Solucionador Design Squad

Severidade: LOW
Categoria: clickup
Erro: "429 Rate limit exceeded"

Contexto:
- Cliente: Dra. Camila
- Agente: orquestrador
- Task: 86def456

Fallback tentado: clickup-rate-limit
Resultado: Resolvido após retry #2 (60s backoff)
```
