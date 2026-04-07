---
task: Gerar Moodboard
responsavel: "@pesquisador-ref"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Cliente + estilo desejado
  - Referencias selecionadas (opcional)
Saida: |
  - Moodboard compilado com referencias curadas
  - Links + thumbnails + tags
Checklist:
  - "[ ] Usar moodboard Stark como base"
  - "[ ] Buscar referencias adicionais por estilo"
  - "[ ] Curar selecao (8-15 referencias)"
  - "[ ] Organizar por categoria (cor, layout, tipografia)"
  - "[ ] Gerar compilado visual"
---

# *moodboard

Gera um moodboard curado para um cliente/projeto combinando referencias do Stark com buscas por estilo.

## Uso

```
*moodboard --cliente "Dra. Camila" --estilo "clean e sofisticado"
*moodboard "Moodboard para LP da Clinica Bella Vita estilo bold"
```

## Fluxo

1. Usar moodboard Stark (https://www.behance.net/moodboard/205367489/STARK-REF) como base
2. Buscar referencias adicionais por estilo desejado
3. Se referencias pre-selecionadas foram fornecidas, incluir
4. Curar selecao final: 8-15 referencias
5. Organizar por categoria:
   - Cor (paletas e combinacoes)
   - Layout (estruturas e composicoes)
   - Tipografia (fontes e hierarquia)
6. Gerar compilado visual com links e thumbnails

## Regras

- Sempre partir do moodboard Stark como base
- Curar entre 8-15 referencias (nem pouco nem excessivo)
- Organizar por categoria para facilitar consulta
- Incluir tags de estilo em cada referencia
- Variar fontes: Behance, Dribbble, Pinterest
