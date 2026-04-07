---
task: Historico de Fotos
responsavel: "@brand-guardian"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Nome do cliente
  - Periodo (opcional — padrao: ultimos 60 dias)
Saida: |
  - Lista de fotos ja usadas com datas e tipo de post
  - Alerta se foto solicitada ja foi usada recentemente
Checklist:
  - "[ ] Consultar photos_used no YAML do cliente"
  - "[ ] Filtrar por periodo solicitado"
  - "[ ] Verificar se ha repeticao potencial"
  - "[ ] Retornar lista formatada"
---

# *historico-fotos

Consulta historico de fotos usadas por cliente para evitar repeticao no feed.

## Uso

```
*historico-fotos "Dra. Camila"
*historico-fotos --cliente "Dr. Cadu" --periodo "90 dias"
*historico-fotos "Bella Vita ultimos 30 dias"
```

## Fluxo

1. Receber nome do cliente e periodo (padrao: 60 dias)
2. Consultar campo photos_used no YAML do cliente (data/brands/[cliente].yaml)
3. Filtrar fotos pelo periodo solicitado
4. Verificar se ha repeticao potencial com fotos sugeridas
5. Retornar lista formatada com: URL da foto, data de uso, tipo de post, plataforma

## Regras

- Alertar se uma foto ja foi usada nos ultimos 60 dias
- Sem repeticao de fotos ja usadas no feed e obrigatorio
- Fotos de antes/depois: partes intimas devem estar cobertas com logo do cliente
- Retornar lista ordenada por data (mais recente primeiro)
