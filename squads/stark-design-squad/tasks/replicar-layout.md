---
task: Replicar Layout
responsavel: "@designer-figma"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Frame de referencia (link ou nome)
  - Novo cliente/data de destino
Saida: |
  - Novo frame replicado com identidade adaptada
Checklist:
  - "[ ] Acessar frame de referencia"
  - "[ ] Consultar Brand Guardian do novo cliente"
  - "[ ] Replicar estrutura mantendo fidelidade"
  - "[ ] Adaptar cores, fontes e imagens"
  - "[ ] Verificar naming padrao"
  - "[ ] Enviar para QA"
---

# *replicar-layout

Replica um layout existente no Figma para outro cliente ou data, adaptando identidade visual.

## Uso

```
*replicar-layout --ref "Frame Dra. Camila Carrossel" --destino "Dr. Cadu" --data "2026-04-01"
*replicar-layout "Replicar carrossel da Bella Vita para Clinica Renova"
```

## Fluxo

1. Acessar frame de referencia no Figma
2. Consultar Brand Guardian para guidelines do novo cliente
3. Duplicar estrutura do frame mantendo fidelidade ao layout
4. Adaptar: cores (paleta do novo cliente), fontes, imagens, logo
5. Renomear com naming padrao: [cliente]-[tipo]-[AAAAMMDD]-v[numero]
6. Enviar para QA de Qualidade

## Regras

- Nunca alterar o frame original de referencia
- Sempre consultar Brand Guardian do novo cliente antes de adaptar
- Manter mesma estrutura e hierarquia do layout original
- Naming: [cliente]-[tipo]-[AAAAMMDD]-v[numero]
- Toda entrega passa pelo QA antes de ser finalizada
