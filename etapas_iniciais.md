# Início Rápido - Carteira Digital API

## 📋 Checklist de Instalação

### 1️⃣ Banco de Dados MySQL

Execute os scripts SQL nesta ordem (como usuário root):

```sql
-- 1. Criar banco e usuário
source sql/01_criar_banco_e_usuario.sql

-- 2. Criar tabelas
source sql/02_criar_tabelas.sql

-- 3. Popular moedas
source sql/03_popular_moedas.sql
```

**Ou copie e cole o conteúdo de cada arquivo no seu cliente MySQL.**

### 2️⃣ Ambiente Python

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3️⃣ Executar a API

```bash
uvicorn app.main:app --reload
```

### 4️⃣ Acessar Documentação

Abra no navegador: **http://127.0.0.1:8000/docs**

---

## 🚀 Teste Rápido

1. Acesse http://127.0.0.1:8000/docs
2. Clique em **POST /carteiras** → **Try it out** → **Execute**
3. Copie o `endereco_carteira` e `chave_privada` retornados
4. Clique em **POST /carteiras/{endereco_carteira}/depositos** → **Try it out**
5. Cole o endereço, preencha:
   ```json
   {
     "moeda_id": "BRL",
     "valor": 1000
   }
   ```
6. Execute e veja o depósito sendo realizado!
7. Consulte os saldos em **GET /carteiras/{endereco_carteira}/saldos**

---

## 📁 Estrutura de Arquivos

```
carteira_digital/
├── sql/                           # Scripts do banco de dados
│   ├── 01_criar_banco_e_usuario.sql
│   ├── 02_criar_tabelas.sql
│   └── 03_popular_moedas.sql
├── app/                           # Código da API
│   ├── main.py                    # Endpoints FastAPI
│   ├── services.py                # Lógica de negócio
│   ├── database.py                # Conexão MySQL
│   ├── models.py                  # Modelos Pydantic
│   ├── utils.py                   # Funções auxiliares
│   └── config.py                  # Configurações
├── .env                           # Variáveis de ambiente
├── requirements.txt               # Dependências Python
├── README.md                      # Documentação completa
├── GUIA_DE_TESTES.md             # Exemplos de teste
└── INICIO_RAPIDO.md              # Este arquivo
```

---

## ⚙️ Configurações Importantes (.env)

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=wallet_api_homolog
DB_PASSWORD=api123
DB_NAME=wallet_homolog
TAXA_SAQUE_PERCENTUAL=0.01         # 1%
TAXA_CONVERSAO_PERCENTUAL=0.02     # 2%
TAXA_TRANSFERENCIA_PERCENTUAL=0.01 # 1%
```

---

## 🎯 Funcionalidades Implementadas

✅ Criação de carteiras com chaves pública/privada  
✅ Consulta de informações e saldos  
✅ Depósitos (sem taxa, sem autenticação)  
✅ Saques (com taxa, requer chave privada)  
✅ Conversão entre moedas (integração Coinbase)  
✅ Transferências entre carteiras  
✅ Suporte a 5 moedas: BTC, ETH, SOL, USD, BRL  
✅ Validação de chave privada por hash SHA-256  
✅ Histórico de todas as operações  
✅ Documentação interativa (Swagger)

---

## 🔒 Segurança

- Chave privada retornada **apenas na criação**
- Armazenamento de **hash SHA-256** (não texto puro)
- Usuário do banco com **permissões limitadas** (apenas DML)
- Validações de saldo antes de operações
- Transações atômicas no banco de dados

---

## 📚 Documentação Adicional

- **README.md**: Documentação completa e detalhada
- **GUIA_DE_TESTES.md**: Exemplos práticos de uso da API
- **Swagger UI**: http://127.0.0.1:8000/docs (após iniciar a API)
