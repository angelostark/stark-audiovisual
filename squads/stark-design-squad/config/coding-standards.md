# Coding Standards — Stark Design Squad

## Convenções de Nomenclatura

### Frames no Figma
```
[DATA] - [NOME DO DRIVE]
```
Exemplos: `2026-03-17 - Stark`, `2026-03-20 - Nike Brasil`

### Arquivos de Entrega
```
[cliente]-[tipo]-[AAAAMMDD]-v[numero]
```
Exemplos: `stark-carrossel-20260317-v1`, `dentalPrime-capa-20260320-v2`

### Componentes Atomic Design (Web Designer LP)
```
[nível]-[tipo]-[cliente]-[variante]
```
Níveis: `atomo`, `molecula`, `organismo`, `template`, `pagina`
Exemplos: `atomo-botao-primary-v1`, `organismo-hero-fitlife-escuro`

### Componentes LP (nomenclatura de pasta)
```
[tipo]-[cliente]-[variante]
```
Exemplos: `hero-dentalPrime-v1`, `cta-fitlife-escuro`

## Padrões de Arquivo

| Tipo | Formato | Resolução |
|------|---------|-----------|
| Estático (feed) | PNG | 1080x1350px |
| Stories/Reels | PNG | 1080x1920px |
| Fotografia | JPG | Resolução original |
| Assets exportados | PNG | Conforme necessário |

## Estrutura de Pastas

### Google Drive
```
Clientes / [nome_drive] / Cronograma de Conteúdo / Artes / [ano] / [mês] / [data]
```

### Figma — Design
```
[Nome do Cliente]
  └─ Assets
  └─ Templates
  └─ Entregas
       └─ [AAAA-MM] Mês de Referência
            └─ Carrosseis
            └─ Estáticos
            └─ Capas
```

### Figma — Landing Pages (Atomic)
```
[LP - Nome do Cliente]
  └─ 01-Atomos/
  └─ 02-Moleculas/
  └─ 03-Organismos/
  └─ 04-Templates/
  └─ 05-Paginas/
```

## Regras de Qualidade

- Versões reprovadas devem ser arquivadas, nunca deletadas
- Toda entrega exportada como PNG para estáticos, JPG para fotografias
- Frame salvo corretamente na pasta do cliente no Drive
- Nenhum post marcado como entregue sem QA aprovado
