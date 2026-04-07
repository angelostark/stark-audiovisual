---
task: Avaliar Entrega
responsavel: "@qa-qualidade"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Imagem(ns) do post/LP/capa
  - Regras Stark aplicaveis
  - Brand guidelines do cliente (via Brand Guardian)
Saida: |
  - Nota 0-10 por criterio
  - Nota geral ponderada
  - Lista de regras quebradas
  - Veredito: Premium / Aprovado / Ressalvas / Reprovado
Checklist:
  - "[ ] Avaliar Criatividade e inovacao (25%)"
  - "[ ] Avaliar Elementos obrigatorios (25%)"
  - "[ ] Verificar Regras Stark — itens proibidos (25%)"
  - "[ ] Avaliar Hierarquia e legibilidade (15%)"
  - "[ ] Avaliar Acabamento tecnico (10%)"
  - "[ ] Calcular nota ponderada"
  - "[ ] Gerar veredito"
  - "[ ] Se reprovado: gerar laudo completo"
---

# *avaliar

Avalia entregas de design com 5 criterios ponderados (nota 0-10) e emite veredito seguindo o padrao Stark.

## Uso

```
*avaliar --imagem "link_ou_path_da_imagem"
*avaliar "Avaliar carrossel Dra. Camila - Rinoplastia"
```

## Fluxo

1. Receber imagem(ns) da entrega
2. Consultar Brand Guardian para guidelines do cliente
3. Avaliar 5 criterios ponderados:
   - **Criatividade e inovacao (25%)**: Layout original, nao repete estilo dos ultimos 3 posts, sem banco de imagens
   - **Elementos obrigatorios da capa (25%)**: LOGO/ICON, Titulo+Subtitulo, CTA, imagem de apoio, foto Doctor(a)
   - **Regras Stark (25%)**: Nenhum item proibido presente
   - **Hierarquia e legibilidade (15%)**: Fluxo de leitura claro, elementos dentro do grid 1080x1350px
   - **Acabamento tecnico (10%)**: Resolucao correta, alinhamentos limpos, exportacao sem artefatos
4. Calcular nota ponderada geral
5. Emitir veredito:
   - 9-10: Aprovado Premium (entra no Ranking)
   - 7-8: Aprovado (segue para entrega)
   - 5-6: Aprovado com ressalvas (lista de ajustes)
   - <5 ou >3 regras quebradas: Reprovado (laudo + retrabalho)

## Regras

- Se mais de 3 regras Stark forem quebradas: reprovar imediatamente
- Itens PROIBIDOS: capa so texto + cor solida sem CTA, ilustracao escondida, fotos estilo banco de imagens, elementos fora do grid, repeticao de layout nos ultimos 3 posts, grade de quadrados com resultados, uso excessivo de degrades
- Ultimo card do carrossel obrigatorio: CTA em destaque + foto cliente + LOGO ou ICON
- Antes/depois: partes intimas cobertas com logo do cliente
