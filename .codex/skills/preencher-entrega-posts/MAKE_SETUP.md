# Tutorial: Configuração Make.com + Google Drive

Para deixar a automação de Entregas do ClickUp 100% autônoma (sem precisar rodar o Claude para baixar JSONs), usaremos o **Make.com** para ler o ClickUp e salvar o resultado no **Google Drive**. O Script Python que criamos baixará esse arquivo automaticamente.

## Passo a Passo no Make.com

### 1. Criar um Novo Cenário (Scenario)
Crie um novo cenário e adicione o primeiro módulo.

### 2. Módulo 1: ClickUp (Make an API Call)
Esta é a maneira mais limpa de puxar todos os dados brutos de uma vez, do jeito exato que o script Python já sabe ler.
- **App:** ClickUp
- **Action:** Make an API Call
- **URL:** `/api/v2/list/901324888130/task`
  *(Nota: `901324888130` é o ID da lista "Agenda de Postagem 3.0" que identificamos nos seus testes. Se quiser puxar de um Folder ou Space maior, troque a URL da API do ClickUp).*
- **Method:** `GET`
- **Headers/Body:** Pode deixar vazio.

### 3. Módulo 2: Google Drive (Upload a File)
Conecte este módulo logo em seguida. Ele vai salvar a resposta do ClickUp num arquivo de texto.
- **App:** Google Drive
- **Action:** Upload a File
- **Connection:** Conecte na mesma conta Google onde está o seu `credentials.json` (ou na conta corporativa que a automação tem acesso de leitura).
- **Destination:** Selecione uma pasta no seu Drive (ex: `Automacoes/ClickUp`).
- **File Name:** `clickup_raw_atual.json` (Exatamente este nome).
- **Data:** Selecione o conteúdo bruto retornado pelo módulo 1 (Geralmente a variável se chama `Body`).

### 4. Configurar o Agendamento (Schedule)
No canto inferior esquerdo do Make, clique no relógio e configure para rodar:
- **Days of the week:** Wednesday (Quarta-feira)
- **Time:** 19:30 (meia-hora antes do seu Mac processar a planilha).

---
**✅ Pronto!**
Quando você salvar e ativar ("ON"), o Make Fará o download invisível do ClickUp para o seu Google Drive toda quarta-feira.
O script Python no seu computador será atualizado para ler esse arquivo do seu Google Drive.
