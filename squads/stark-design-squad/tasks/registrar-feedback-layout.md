---
task: Registrar Feedback Layout
responsavel: "@orquestrador"
responsavel_type: agent
atomic_layer: task
squad: stark-design-squad
elicit: true
Entrada: |
  - Layout ID ou cliente + descricao para localizar
  - Feedback (texto livre)
  - Fonte: cliente, copy, gestor
  - Observacoes (opcional)
Saida: |
  - Planilha Layout Index atualizada com feedback
  - Confirmacao com layout ID e feedback registrado
Checklist:
  - "[ ] Identificar layout no indice"
  - "[ ] Validar fonte do feedback"
  - "[ ] Atualizar colunas Feedback Externo e Fonte Feedback"
  - "[ ] Se houver observacoes: atualizar coluna Observacoes"
  - "[ ] Confirmar registro ao usuario"
---

# *registrar-feedback

Registra feedback externo (cliente, copy, gestor) em um layout ja indexado. Permite capturar insights para melhoria continua.

## Uso

```
*registrar-feedback "Cliente pediu tom mais quente" --fonte cliente --layout drgeorge-estatico-20260331-v1
*registrar-feedback "Copy sugeriu menos texto" --fonte copy --cliente "Dr George"
*registrar-feedback "Gestor: muito bom, manter esse estilo" --fonte gestor --layout dracamila-carrossel-20260328-v1
```

## Planilha

- **ID**: `1kZOi4zw8ih8bI7mJsiQXYyMKFvCPotBkzWnpIP3B1Sg`
- **Colunas afetadas**: Feedback Externo (N), Fonte Feedback (O), Observacoes (R)

## Fluxo

1. Receber feedback + fonte + identificacao do layout
2. Localizar layout no indice:
   - Se `--layout ID` fornecido: busca direta por ID na aba correspondente
   - Se `--cliente` fornecido sem ID: listar layouts recentes do cliente e pedir selecao
   - Se nenhum: perguntar cliente e ID
3. Validar fonte do feedback:
   - Aceitos: `cliente`, `copy`, `gestor`
   - Se nao informado: perguntar
4. Atualizar planilha:
   - Se campo "Feedback Externo" ja tem conteudo: **concatenar** com separador " | "
     Ex: "Cliente aprovou" → "Cliente aprovou | Cliente pediu tom mais quente"
   - Se campo "Fonte Feedback" ja tem conteudo: **concatenar** com separador ", "
     Ex: "cliente" → "cliente, copy"
   - Se `--observacoes` fornecido: atualizar coluna Observacoes (mesmo concat)
5. Confirmar ao usuario: "Feedback registrado no layout {id} (fonte: {fonte})"

## Fontes de Feedback Aceitas

| Fonte | Descricao | Quando usar |
|-------|-----------|-------------|
| `cliente` | Feedback direto do cliente (via ClickUp, email, WhatsApp) | Quando o cliente comenta sobre a arte |
| `copy` | Feedback do time de conteudo/copywriting | Quando copy sugere ajustes de texto/tom |
| `gestor` | Feedback do gestor (Angelo) ou lideranca | Quando lideranca avalia a entrega |

## Captura via ClickUp (semi-automatico)

Quando o feedback vier de um comentario no ClickUp:

1. Receber task ID do ClickUp
2. Buscar comentarios via `clickup_get_task_comments`
3. Extrair ultimo comentario relevante
4. Identificar autor como fonte (cliente/copy/gestor)
5. Registrar na planilha automaticamente

```
*registrar-feedback --clickup-task "abc123" --layout drgeorge-estatico-20260331-v1
```

## Regras

- Layout deve existir no indice — se nao encontrado, informar e sugerir *indexar-layout
- Feedback e texto livre — nao ha validacao de conteudo
- Fonte e obrigatoria: cliente, copy ou gestor
- Feedbacks sao ACUMULATIVOS — nunca sobrescrever, sempre concatenar
- Separador entre feedbacks: " | "
- Separador entre fontes: ", "
- Maximo 500 caracteres por feedback individual
