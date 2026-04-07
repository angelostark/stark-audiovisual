---
task: Buscar Layout
responsavel: "@designer-figma"
responsavel_type: agent
also_used_by: ["@orquestrador"]
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Cliente (obrigatorio)
  - Tipo (opcional): estatico, carrossel, capa, stories, lp
  - Tags (opcional): antes_depois, informativo, promocional, etc.
  - Nota minima (opcional): float 0-10
  - Subtipo (opcional): antes_depois, informativo, promocional
Saida: |
  - Lista de layouts encontrados em JSON
  - Cada layout com ID, Figma URL, nota QA, tags, data
  - Ordenados por nota QA (desc) e data (desc)
Checklist:
  - "[ ] Identificar cliente e montar filtros"
  - "[ ] Buscar na planilha Layout Index (aba do cliente)"
  - "[ ] Filtrar por tipo, subtipo, tags e nota minima"
  - "[ ] Ordenar por nota QA desc, data desc"
  - "[ ] Retornar resultados formatados"
  - "[ ] Se vazio: informar que nao ha layouts indexados"
---

# *buscar-layout

Busca layouts ja criados no indice por cliente, tipo, tags e nota minima. Permite reutilizar e se inspirar em trabalhos anteriores.

## Uso

```
*buscar-layout "Dr George" --tipo estatico
*buscar-layout "Dra Camila" --tipo carrossel --nota-minima 8
*buscar-layout "Dr George" --tags antes_depois,foto_real
*buscar-layout "Clinica Bella" --subtipo promocional
```

## Planilha

- **ID**: `1kZOi4zw8ih8bI7mJsiQXYyMKFvCPotBkzWnpIP3B1Sg`
- **Estrutura**: uma aba por cliente (ex: "Dr George", "Dra Camila")
- **Colunas**: ID, Tipo, Subtipo, Data Criacao, Designer, Figma URL, Figma Node ID, Drive Path, Formato, Nota QA, Veredito QA, Refacoes, Tempo (dias), Feedback Externo, Fonte Feedback, Tags, Engajamento, Observacoes

## Fluxo

1. Receber filtros do usuario (cliente obrigatorio)
2. Acessar planilha Layout Index via Google Sheets API
3. Localizar aba do cliente (case-insensitive)
4. Se aba nao existe: informar "Nenhum layout indexado para {cliente}"
5. Aplicar filtros:
   - `--tipo`: coluna Tipo (match exato)
   - `--subtipo`: coluna Subtipo (match exato)
   - `--tags`: coluna Tags (match parcial, OR entre tags)
   - `--nota-minima`: coluna Nota QA >= valor
6. Ordenar resultados: Nota QA desc, Data Criacao desc
7. Retornar em formato tabela + JSON:
   ```json
   {
     "id": "drgeorge-estatico-20260331-v1",
     "tipo": "estatico",
     "subtipo": "antes_depois",
     "data": "2026-03-31",
     "designer": "Joao Andare",
     "figma_url": "https://figma.com/...",
     "nota_qa": 8.5,
     "veredito_qa": "Aprovado",
     "refacoes": 0,
     "tags": ["antes_depois", "cirurgia", "foto_real"],
     "feedback": "Cliente aprovou de primeira"
   }
   ```
8. Se houver mais de 10 resultados: paginar (mostrar top 10 + indicar total)

## Regras

- Cliente e obrigatorio — se nao informado, perguntar
- Busca case-insensitive no nome da aba
- Se aba nao existe: retornar mensagem amigavel, nao erro
- Maximo 10 resultados por pagina
- Incluir link do Figma clicavel no resultado
- Ordem padrao: nota QA desc, depois data desc
