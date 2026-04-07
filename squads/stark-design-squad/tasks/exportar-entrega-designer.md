---
task: Exportar Entrega Designer
responsavel: "@designer-figma"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Frame aprovado pelo QA
Saida: |
  - PNGs no Drive + comentario no ClickUp + notificacao
Checklist:
  - "[ ] Confirmar aprovacao do QA"
  - "[ ] Executar fluxo figma-export-para-drive"
  - "[ ] Registrar uso de fotos no Brand Guardian"
---

# *exportar-entrega

Exporta entrega aprovada pelo QA para o Drive e registra no ClickUp. Reutiliza o skill `figma-export-para-drive`.

## Uso

```
*exportar-entrega --frame "Frame aprovado Dra. Camila"
*exportar-entrega "Exportar e entregar carrossel aprovado"
```

## Fluxo

1. Confirmar que o QA aprovou a entrega (nota >= 7)
2. Executar fluxo completo do skill figma-export-para-drive:
   - Exportar PNGs do Figma
   - Upload para Drive na pasta do cliente
   - Comentar na subtarefa do ClickUp com link
   - Atualizar status para "edicao concluida"
3. Registrar fotos usadas no Brand Guardian para controle de historico

## Regras

- Nunca exportar sem aprovacao do QA
- Sempre registrar fotos usadas no Brand Guardian apos entrega
- Seguir estrutura de pastas do Drive do cliente
- Notificar responsavel da tarefa mae via ClickUp
