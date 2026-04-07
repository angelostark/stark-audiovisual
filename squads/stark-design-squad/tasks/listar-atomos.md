---
task: Listar Atomos
responsavel: "@web-designer-lp"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: false
Entrada: |
  - Cliente (opcional — se nao informar, lista todos)
  - Nivel Atomic (opcional — filtra por nivel)
Saida: |
  - Lista de componentes disponiveis por nivel
  - Status de uso: ativo, depreciado, novo
Checklist:
  - "[ ] Navegar estrutura de pastas Atomic"
  - "[ ] Listar por nivel (atomos -> moleculas -> organismos)"
  - "[ ] Indicar quais sao genericos vs especificos de cliente"
  - "[ ] Formatar como tabela para facil consulta"
---

# *listar-atomos

Lista todos os componentes disponíveis na biblioteca Atomic Design, filtrados por cliente ou nível.

## Uso

```
*listar-atomos
*listar-atomos --cliente "Bella Vita"
*listar-atomos --nivel "molecula"
*listar-atomos --cliente "Dr. Cadu" --nivel "organismo"
```

## Fluxo

1. Navegar estrutura de pastas Atomic no Figma:
   - 01-Atomos/
   - 02-Moleculas/
   - 03-Organismos/
2. Listar componentes por nivel hierarquico
3. Classificar cada componente:
   - Generico (reutilizavel para qualquer cliente)
   - Especifico de cliente (paleta/estilo customizado)
4. Indicar status: ativo, depreciado, novo
5. Formatar como tabela para consulta rapida

## Regras

- Se nenhum filtro fornecido: listar todos os componentes
- Ordem: atomos primeiro, depois moleculas, depois organismos
- Indicar claramente quais sao genericos vs especificos
- Incluir contagem total por nivel
