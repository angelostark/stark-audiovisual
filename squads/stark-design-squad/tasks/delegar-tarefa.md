---
task: Delegar Tarefa
responsavel: "@orquestrador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Pedido em linguagem natural do gestor
  - Contexto: cliente, urgencia, tipo de entrega
Saida: |
  - Briefing completo delegado ao agente correto
  - Estimativa de tempo informada ao gestor
  - Task no ClickUp consultada/criada
Checklist:
  - "[ ] Interpretar pedido e identificar tipo de entrega"
  - "[ ] Confirmar cliente com o gestor"
  - "[ ] Consultar ClickUp para tasks abertas"
  - "[ ] Consultar Brand Guardian para guidelines do cliente"
  - "[ ] Montar briefing completo para o agente executor"
  - "[ ] Acionar agente correto"
  - "[ ] Informar estimativa de tempo ao gestor"
---

# *delegar

Interpreta pedidos do gestor em linguagem natural, identifica o tipo de entrega e delega ao agente correto do squad com briefing completo.

## Uso

```
*delegar "Criar carrossel de rinoplastia para Dra. Camila"
*delegar "Preciso de uma capa de reels para o Dr. Cadu, urgente"
*delegar "LP nova para a clinica Bella Vita"
```

## Fluxo

1. Receber pedido do gestor
2. Interpretar tipo de entrega (post, LP, capa, etc.)
3. Confirmar cliente (se ambiguo, perguntar — max 3 perguntas)
4. Consultar ClickUp para tasks existentes do cliente
5. Consultar Brand Guardian para guidelines atualizadas
6. Montar briefing estruturado com: cliente, tipo, prazo, guidelines, referencias
7. Acionar agente executor correto:
   - Post/carrossel/estatico → Designer Figma
   - Landing page → Web Designer LP
   - Capa de reels → Construtor Capa Reels
8. Informar estimativa de tempo ao gestor

## Regras

- Nunca executar tarefas de design — sempre delegar
- Maximo 3 perguntas de clarificacao por pedido
- Sempre consultar Brand Guardian antes de delegar
- Toda entrega passa pelo QA antes de ser finalizada
- Informar estimativa de tempo ao gestor apos delegacao
