---
task: Registrar Uso
responsavel: "@brand-guardian"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Foto/asset usado
  - Cliente
  - Data de uso
  - Tipo de post
Saida: |
  - Historico atualizado no YAML do cliente
Checklist:
  - "[ ] Validar que a foto nao foi usada nos ultimos 60 dias"
  - "[ ] Adicionar entrada em photos_used"
  - "[ ] Salvar YAML atualizado"
---

# *registrar-uso

Registra o uso de uma foto ou asset no historico do cliente para evitar repeticoes futuras.

## Uso

```
*registrar-uso --cliente "Dra. Camila" --foto "url_da_foto" --tipo "carrossel"
*registrar-uso "Registrar foto usada no reels Dr. Cadu"
```

## Fluxo

1. Receber dados: foto/asset, cliente, data de uso, tipo de post
2. Validar que a foto nao foi usada nos ultimos 60 dias
3. Se ja usada: alertar e pedir confirmacao para prosseguir
4. Adicionar entrada no campo photos_used do YAML do cliente:
   - url: URL da foto
   - date: YYYY-MM-DD
   - post_type: tipo do post (carrossel, estatico, capa, reels)
   - platform: plataforma (instagram, etc.)
5. Salvar YAML atualizado

## Regras

- Sempre validar antes de registrar: foto nao pode ter sido usada nos ultimos 60 dias
- Se houver conflito: alertar o designer/orquestrador antes de registrar
- Formato da data: YYYY-MM-DD
- Campo obrigatorio: url, date, post_type
