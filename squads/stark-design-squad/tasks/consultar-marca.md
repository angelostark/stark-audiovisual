---
task: Consultar Marca
responsavel: "@brand-guardian"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Nome do cliente
Saida: |
  - Paleta de cores (primary, secondary, accent)
  - Tipografia (heading, body)
  - Tom visual
  - Variantes de logo
Checklist:
  - "[ ] Localizar data/brands/[cliente].yaml"
  - "[ ] Se nao existir: criar template e solicitar preenchimento"
  - "[ ] Retornar guidelines completas"
  - "[ ] Alertar se guidelines estao incompletas"
---

# *consultar-marca

Consulta guidelines de marca de um cliente especifico — paleta, tipografia, tom visual e logos.

## Uso

```
*consultar-marca "Dra. Camila"
*consultar-marca --cliente "Dr. Cadu"
*consultar-marca "Clinica Bella Vita"
```

## Fluxo

1. Receber nome do cliente
2. Localizar arquivo data/brands/[cliente].yaml
3. Se nao existir: criar template YAML e solicitar preenchimento ao gestor
4. Retornar guidelines completas:
   - Paleta de cores: primary, secondary, accent (hex)
   - Tipografia: heading, body
   - Tom visual
   - Variantes de logo disponiveis
5. Alertar se algum campo obrigatorio estiver vazio

## Regras

- Sempre consultar YAML do cliente antes de qualquer criacao
- Se guidelines incompletas: alertar antes de prosseguir
- Manter pelo menos 3 variantes de logo por cliente
- Template YAML segue schema padrao do squad
