# Setup — Google APIs (Sheets + Drive)

## Passo 1: Criar projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Clique em **Selecionar projeto** → **Novo projeto**
3. Nome: `Stark Metas AV`
4. Clique em **Criar**

## Passo 2: Ativar Google Sheets API

1. No menu lateral: **APIs e Serviços** → **Biblioteca**
2. Pesquise: `Google Sheets API`
3. Clique nela → **Ativar**
4. Pesquise também: `Google Drive API`
5. Clique nela → **Ativar**

## Passo 3: Criar conta de serviço

1. No menu lateral: **APIs e Serviços** → **Credenciais**
2. Clique em **Criar credenciais** → **Conta de serviço**
3. Nome: `metas-av-bot`
4. Clique em **Criar e continuar**
5. Role: selecione **Editor** → **Continuar** → **Concluir**

## Passo 4: Gerar chave JSON

1. Na lista de contas de serviço, clique em `metas-av-bot`
2. Aba **Chaves** → **Adicionar chave** → **Criar nova chave**
3. Tipo: **JSON**
4. Clique em **Criar** — vai baixar um arquivo `.json`
5. **Renomeie** o arquivo para `credentials.json`
6. **Mova** para: `automacoes/credentials.json`

## Passo 5: Compartilhar planilhas com o bot

O arquivo `credentials.json` contém um campo `client_email` com algo tipo:
```
metas-av-bot@stark-metas-av.iam.gserviceaccount.com
```

Copie esse e-mail e compartilhe CADA planilha com ele:

1. **Planilha de Metas** → Compartilhar → colar o email → permissão: **Editor**
2. **Planilha de Layouts** → Compartilhar → colar o email → permissão: **Leitor**
3. **Planilha de Entregas** → Compartilhar → colar o email → permissão: **Leitor**

## Passo 5.1: Compartilhar pasta "Clientes" do Drive com o bot

Para a skill **Figma → Drive → ClickUp** funcionar, o bot precisa acessar as pastas do Drive:

1. Abra o Google Drive
2. Navegue até a pasta **"Clientes"** (pasta raiz dos clientes)
3. Clique com botão direito → **Compartilhar**
4. Cole o email do service account (mesmo do Passo 5)
5. Permissão: **Editor** (precisa criar subpastas e fazer upload)
6. Clique em **Enviar**

> O bot só terá acesso às pastas compartilhadas com ele. Nada mais do Drive fica visível.

## Passo 6: Instalar dependências Python

```bash
pip install gspread google-auth google-api-python-client
```

## Passo 7: Testar

### Testar Metas AV:
```bash
python3 automacoes/metas_av.py --dry-run
```

Se aparecer o resumo com os valores calculados, está tudo funcionando!

### Testar Upload Drive:
```bash
python3 automacoes/upload_drive.py --client "Stark" --date "2026-03-17" --dry-run
```

Se navegar toda a hierarquia de pastas sem erro, o Drive está configurado!

## Segurança

- **NUNCA** commite o `credentials.json` no git
- O arquivo já está no `.gitignore`
- Se vazar, revogue a chave no Google Cloud Console imediatamente
