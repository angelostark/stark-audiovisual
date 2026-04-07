---
task: Criar Capa Reels
responsavel: "@construtor-capa-reels"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Briefing + foto do Doctor(a)
  - Identidade visual do cliente
  - Texto principal (max 5 palavras)
Saida: |
  - 2 versoes: com texto e sem texto
  - Formatos: 1080x1920 (reels) + 1080x1350 (feed)
Checklist:
  - "[ ] Consultar Brand Guardian para paleta/fontes"
  - "[ ] Verificar fotos ja usadas no feed"
  - "[ ] Aplicar imagem de fundo (personagem/produto)"
  - "[ ] Posicionar texto principal (>80pt, contraste alto)"
  - "[ ] Adicionar elemento de atencao (seta/emoji/grafismo)"
  - "[ ] Verificar area segura (<1600px)"
  - "[ ] Verificar maximo 3 cores"
  - "[ ] Gerar versao com texto"
  - "[ ] Gerar versao sem texto"
  - "[ ] Exportar nos 2 formatos"
  - "[ ] Enviar para QA"
---

# *criar-capa

Cria capas de reels otimizadas para clique e parada no scroll, em 2 versoes (com/sem texto) e 2 formatos.

## Uso

```
*criar-capa --cliente "Dr. Cadu" --texto "Rinoplastia Sem Dor" --foto "link_foto"
*criar-capa "Capa para reels de lipoaspiracao Dra. Camila"
```

## Fluxo

1. Consultar Brand Guardian para paleta e fontes do cliente
2. Verificar historico de fotos para evitar repeticao no feed
3. Aplicar imagem de fundo com personagem ou produto (evitar genericos)
4. Posicionar texto principal: max 5 palavras, fonte >80pt, contraste alto
5. Adicionar elemento de atencao: seta, emoji ou grafismo direcionando olhar
6. Verificar area segura: nenhum elemento importante abaixo de 1600px
7. Verificar paleta: maximo 3 cores seguindo identidade do cliente
8. Gerar versao COM texto
9. Gerar versao SEM texto
10. Exportar: 1080x1920 (reels) + 1080x1350 (feed)
11. Enviar para QA

## Regras

- Texto principal: maximo 5 palavras, fonte acima de 80pt, contraste alto
- Imagem de fundo: sempre com personagem ou produto — evitar genericos
- Elemento de atencao obrigatorio: seta, emoji ou grafismo
- Area segura: nenhum elemento importante abaixo de 1600px
- Paleta: maximo 3 cores seguindo identidade do cliente
- Sempre criar 2 versoes: com e sem texto
- Formatos: 1080x1920 (reels) + 1080x1350 (feed)
