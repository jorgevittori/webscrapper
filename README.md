# Web Scraper para Monitoramento de Preços - Mercado Livre

Este projeto é um **web scraper** que monitora os preços de um ou mais produtos específicos no **Mercado Livre**. Quando configurada uma rotina de monitoramento, é possível acompanhar a evolução dos preços ao longo do tempo. Se executado em ambiente que permita, é criado um banco sqlite3 na aplicação.

## Funcionalidades

- **Monitoramento de preços**: O scraper coleta informações sobre o preço atual, preço anterior e preço de parcelamento de um produto.
- **Envio de notificações**: Envia mensagens via **Telegram** quando um novo preço é detectado.
- **Banco de dados**: Armazena os dados coletados em um banco de dados **SQLite** para histórico de preços.
- **Suporte para múltiplos ambientes**: O código suporta ambientes de desenvolvimento (`staging`) e produção (`prod`), com configuração de variáveis de ambiente através de arquivos `.env`.

## Como usar

### 1. Configuração do ambiente

Antes de executar o script, você precisará configurar algumas variáveis de ambiente:

- **TELEGRAM_TOKEN**: O token do seu bot no Telegram.
- **TELEGRAM_CHAT_IDS**: Lista de IDs de chats do Telegram onde as notificações serão enviadas. Os IDs devem ser separados por vírgula.

Crie um arquivo `.env` na raiz do seu projeto com o seguinte conteúdo:

TELEGRAM_TOKEN=seu_token_aqui

TELEGRAM_CHAT_IDS=seu_chat_id_aqui, outro_chat_id_aqui

Se você estiver no ambiente de **staging**, utilize as variáveis `TELEGRAM_TOKEN_STAGING` e `TELEGRAM_CHAT_IDS_STAGING`.

É importante obter os tokens do seu bot criado através do telegram. Para este projeto, foi usado o [BotFather](https://core.telegram.org/bots/tutorial).

### 2. Instalação das dependências

Para instalar as dependências necessárias, execute o seguinte comando abaixo no inicio do projeto:

pip install -r requirements.txt

### 3. Executando o script

O script é executado automaticamente com base no ambiente configurado. Para rodá-lo no ambiente de **produção** (prod), basta garantir que o valor da variável `enviroment` seja `"prod"`. Para o ambiente de **desenvolvimento** (staging), altere o valor para `"staging"`.

### 4. Como funciona

- O script faz uma requisição HTTP para o produto especificado na variável `product_url`.
- Em seguida, ele faz o parsing da página HTML usando **BeautifulSoup** para extrair o nome do produto, o preço antigo, o novo preço e o preço de parcelamento.
- O preço é então comparado com os preços armazenados no banco de dados SQLite para verificar se houve alguma alteração.
- Caso o preço tenha mudado, o script envia uma mensagem para o Telegram com as informações do produto e o link para a página do Mercado Livre.
- Os dados do preço são armazenados em um banco de dados SQLite.

### 5. Banco de Dados

O script usa **SQLite** para armazenar os preços coletados. A tabela `prices` armazena as seguintes informações:

- `product_name`: Nome do produto.
- `old_price`: Preço antigo do produto.
- `new_price`: Novo preço do produto.
- `installment_price`: Preço do parcelamento do produto.
- `timestamp`: Data e hora em que o preço foi registrado.

### 6. Dependências

Este projeto usa as seguintes dependências:

- `requests`: Para realizar requisições HTTP.
- `beautifulsoup4`: Para fazer o parsing do HTML.
- `sqlite3`: Para interação com o banco de dados SQLite.
- `pytz`: Para lidar com fuso horário.
- `python-telegram-bot`: Para enviar mensagens via Telegram.

### 7. Notas

- Este projeto foi criado com propósitos educativos.
- É possível monitorar outras URLs desde que sejam configuradas as tags html em que o preço está.
- Não faça requisições indiscriminadas nos sites para não ser bloqueado permanentemente.
- O projeto foi criado no IntelliJ
- Dependendo do ambiente, ao realizar o GET o ip já pode estar bloqueado, como por exemplo "PythonAnywhere".
- Caso tenha melhorias, fique a vontade em enviar um PR para o projeto.

