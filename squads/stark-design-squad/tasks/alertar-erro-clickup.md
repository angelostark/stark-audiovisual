---
task: Alertar Erro no ClickUp
responsavel: "@solucionador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Diagnóstico do erro (categoria, severidade, mensagem)
  - Contexto: cliente, task ClickUp, agente de origem
  - Tipo de alerta: erro não resolvido ou fallback falhou
Saida: |
  - Mensagem postada no ClickUp Chat com @menção ao gestor
  - Confirmação de envio
Checklist:
  - "[ ] Montar mensagem de alerta formatada"
  - "[ ] Identificar task/canal do ClickUp para postar"
  - "[ ] Enviar via ClickUp MCP (send_chat_message)"
  - "[ ] Confirmar envio"
  - "[ ] Registrar alerta no error-log.yaml"
---

# *alertar

Envia alerta formatado no ClickUp Chat com @menção ao gestor quando um erro não pode ser auto-resolvido.

## Uso

```
*alertar "Figma file inacessível" --severity HIGH --cliente "Dra. Camila"
*alertar "Credenciais Drive expiradas" --severity CRITICAL
*alertar "teste" --severity LOW
```

## Fluxo

1. **Montar alerta** — Usar template `templates/alerta-erro-tmpl.md` para formatar mensagem
2. **Identificar destino** — Determinar onde postar:
   - Se tem task ClickUp no contexto: postar como comentário na task
   - Se não tem task: postar no canal geral do squad
3. **Enviar** — Usar ClickUp MCP (`send_chat_message` ou `create_task_comment`)
4. **Confirmar** — Verificar que a mensagem foi postada com sucesso
5. **Registrar** — Atualizar log via `*registrar-erro`

## Formato do Alerta

```
🚨 ALERTA — Solucionador Design Squad

Severidade: [HIGH/CRITICAL]
Categoria: [figma/drive/clickup/sistema]
Erro: [mensagem do erro]

Contexto:
- Cliente: [nome]
- Agente: [agente de origem]
- Task: [link ou ID]

Ação necessária: [descrição do que o gestor precisa fazer]

@Angelo — ação necessária
```

## Regras

- Sempre incluir @menção ao gestor (Angelo) em alertas HIGH e CRITICAL
- Para alertas LOW/MEDIUM: postar sem @menção (apenas informativo)
- Nunca postar mais de 3 alertas do mesmo erro em 1 hora (anti-spam)
- Incluir sugestão de resolução quando disponível
- Se ClickUp MCP indisponível: registrar localmente e tentar novamente depois

## Severidade → Formato

| Severidade | Emoji | @menção | Urgência |
|-----------|-------|---------|----------|
| LOW | ℹ️ | Não | Informativo |
| MEDIUM | ⚠️ | Não | Atenção |
| HIGH | 🚨 | Sim | Ação necessária |
| CRITICAL | 🔴 | Sim | Ação imediata |
