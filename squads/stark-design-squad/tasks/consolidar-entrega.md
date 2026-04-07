---
task: Consolidar Entrega
responsavel: "@orquestrador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Entregas dos agentes executores
  - Laudo do QA
Saida: |
  - Relatorio final ao gestor
  - Status atualizado no ClickUp
  - Mensagem no chat da subtarefa
Checklist:
  - "[ ] Verificar aprovacao do QA"
  - "[ ] Confirmar pasta do cliente no Drive"
  - "[ ] Salvar resultado no Drive"
  - "[ ] Atualizar status no ClickUp"
  - "[ ] Postar mensagem no chat da subtarefa"
  - "[ ] @mencionar responsavel"
  - "[ ] Reportar resultado ao gestor"
---

# *consolidar

Consolida entregas dos agentes executores apos aprovacao do QA — salva no Drive, atualiza ClickUp e reporta ao gestor.

## Uso

```
*consolidar
*consolidar "Entrega do carrossel Dra. Camila"
```

## Fluxo

1. Verificar que o QA aprovou a entrega (nota >= 7)
2. Confirmar pasta do cliente no Google Drive
3. Salvar arquivos finais no Drive na estrutura correta
4. Atualizar status da subtarefa no ClickUp
5. Postar mensagem no chat da subtarefa:
   - "Entrega concluida: [nome] | Nota QA: [nota] | Drive: [link]"
6. @mencionar o responsavel da subtarefa
7. Reportar resultado final ao gestor

## Regras

- Nunca marcar tarefa como concluida sem aprovacao do QA
- Sempre confirmar cliente e pasta no Drive antes de salvar
- Se QA reprovou: postar laudo completo no chat + @designer para retrabalho
- Formato da mensagem: "Entrega concluida: [nome] | Nota QA: [nota] | Drive: [link]"
