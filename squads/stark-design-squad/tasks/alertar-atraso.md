---
task: Alertar Atraso
responsavel: "@orquestrador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Tasks abertas no ClickUp com prazo vencido
Saida: |
  - Alerta postado no chat da task mae
  - Gestor informado
Checklist:
  - "[ ] Filtrar tasks abertas com prazo expirado"
  - "[ ] Identificar responsaveis"
  - "[ ] Postar alerta no chat da task mae"
  - "[ ] Notificar gestor"
---

# *alertar-atraso

Monitora tasks abertas no ClickUp com prazo vencido e envia alertas no chat da task mae + notifica o gestor.

## Uso

```
*alertar-atraso
*alertar-atraso --cliente "Dra. Camila"
```

## Fluxo

1. Consultar ClickUp para tasks abertas com due_date < hoje
2. Filtrar apenas tasks com status diferente de "concluido" e "edicao concluida"
3. Agrupar por responsavel e cliente
4. Postar alerta no chat da task mae no ClickUp
5. Reportar resumo de atrasos ao gestor

## Regras

- Sempre identificar o responsavel antes de alertar
- Formato do alerta: "Atraso: [tarefa] | Responsavel: @[nome] | Vencimento: DD/MM"
- Se houver atraso critico (>48h): destacar como urgente
- Nunca alertar tarefas ja concluidas
