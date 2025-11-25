# Projeto Carteira Digital API

API para gerenciamento de carteiras digitais com suporte a múltiplas moedas, desenvolvida com FastAPI e MySQL.

## Visão Geral

Este projeto implementa uma API RESTful completa para simular o funcionamento de uma carteira digital, permitindo:

-   Criação de carteiras com chaves pública e privada.
-   Consulta de informações e saldos.
-   Operações de depósito, saque, conversão de moedas e transferência entre carteiras.
-   Integração com a API da Coinbase para cotações em tempo real.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados em sua máquina:

-   **Python 3.9+**
-   **MySQL Server 8.0+**


## Estrutura do Projeto

O projeto está organizado da seguinte forma para facilitar a compreensão e manutenção:

```
/carteira_digital
├── sql/                    # Scripts SQL para o banco de dados
│   ├── 01_criar_banco_e_usuario.sql
│   ├── 02_criar_tabelas.sql
│   └── 03_popular_moedas.sql
├── app/                    # Código-fonte da aplicação FastAPI
│   ├── __init__.py
│   ├── config.py           # Carrega variáveis de ambiente
│   ├── database.py         # Gerencia a conexão com o banco
│   ├── main.py             # Endpoints da API (FastAPI)
│   ├── models.py           # Modelos de dados (Pydantic)
│   ├── services.py         # Lógica de negócio
│   └── utils.py            # Funções utilitárias (chaves, hash)
├── .env                    # Arquivo de configuração (NÃO versionar)
├── requirements.txt        # Dependências Python
└── README.md               # Este arquivo
```

## Passo a Passo: Instalação e Execução

Siga estas instruções para configurar e executar o projeto em seu ambiente local.

### 1. Preparar os Arquivos

Copie toda a estrutura de pastas e arquivos gerada para um diretório em sua máquina local.

### 2. Configurar o Banco de Dados (MySQL)

Você precisará executar os scripts SQL na ordem correta. Use um cliente MySQL como o MySQL Workbench, DBeaver ou o terminal.

**a. Script 1: Criar Banco e Usuário**

Execute este script como um usuário com privilégios de administrador (como `root`). Ele criará o banco de dados `wallet_homolog` e o usuário `wallet_api_homolog`.


**b. Script 2: Criar Tabelas**

Agora, conecte-se ao banco `wallet_homolog` e execute o segundo script para criar todas as tabelas necessárias.
`

**c. Script 3: Popular Moedas**

Finalmente, execute o terceiro script para popular a tabela `MOEDA` com os valores iniciais.


### 3. Configurar o Ambiente Python

**a. Crie um Ambiente Virtual**

Abra o terminal na pasta raiz do projeto (`/carteira_digital`) e crie um ambiente virtual. Isso isola as dependências do seu projeto.

```bash
python -m venv venv
```

**b. Ative o Ambiente Virtual**

-   **Windows (cmd):** `venv\Scripts\activate`
-   **Linux/macOS:** `source venv/bin/activate`

Seu terminal deve agora exibir `(venv)` no início da linha.

**c. Instale as Dependências**

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias a partir do arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

O arquivo `.env` já está pré-configurado para o ambiente de desenvolvimento local. Se o seu MySQL estiver em uma porta diferente ou com credenciais diferentes, ajuste este arquivo conforme necessário.

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=wallet_api_homolog
DB_PASSWORD=api123
DB_NAME=wallet_homolog
# ... (outras configurações)
```

### 5. Executar a API

Finalmente, inicie o servidor da API com o Uvicorn. O Uvicorn é um servidor ASGI que executará sua aplicação FastAPI.

```bash
uvicorn app.main:app --reload
```

-   `app.main:app`: Aponta para a instância `app` do FastAPI no arquivo `app/main.py`.
-   `--reload`: Faz com que o servidor reinicie automaticamente sempre que você alterar um arquivo de código, ideal para desenvolvimento.

O servidor estará rodando em `http://127.0.0.1:8000`.

## Acessando a Documentação da API

Com o servidor em execução, abra seu navegador e acesse um dos seguintes URLs para ver a documentação interativa gerada automaticamente pelo FastAPI:

-   **Swagger UI (recomendado):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Nesta interface, você pode visualizar todos os endpoints, seus parâmetros, e até mesmo testá-los diretamente do navegador.
