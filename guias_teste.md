# Guia de Testes da API Carteira Digital

Este documento fornece exemplos práticos de como testar todos os endpoints da API.

## Testando com Swagger UI (Recomendado)

A forma mais fácil de testar é usando a interface Swagger em `http://127.0.0.1:8000/docs`. Lá você pode executar todas as operações diretamente do navegador.

## Testando com cURL ou Postman

Abaixo estão exemplos de requisições que você pode fazer usando cURL no terminal ou importar no Postman.

### 1. Verificar se a API está funcionando

```bash
curl http://127.0.0.1:8000/
```

**Resposta esperada:**
```json
{
  "mensagem": "API de Carteira Digital está funcionando!",
  "versao": "1.0.0",
  "documentacao": "/docs"
}
```

---

### 2. Criar uma Nova Carteira

```bash
curl -X POST http://127.0.0.1:8000/carteiras
```

**Resposta esperada:**
```json
{
  "endereco_carteira": "a1b2c3d4e5f6...",
  "chave_privada": "9876543210abcdef..."
}
```

**⚠️ IMPORTANTE:** Salve o `endereco_carteira` e a `chave_privada` retornados! A chave privada só é exibida neste momento.

---

### 3. Consultar Informações da Carteira

Substitua `{endereco_carteira}` pelo endereço obtido no passo anterior.

```bash
curl http://127.0.0.1:8000/carteiras/{endereco_carteira}
```

**Resposta esperada:**
```json
{
  "endereco_carteira": "a1b2c3d4e5f6...",
  "data_criacao": "2025-11-24T10:30:00",
  "status": "ATIVA"
}
```

---

### 4. Consultar Saldos da Carteira

```bash
curl http://127.0.0.1:8000/carteiras/{endereco_carteira}/saldos
```

**Resposta esperada:**
```json
{
  "endereco_carteira": "a1b2c3d4e5f6...",
  "saldos": [
    {"codigo": "BRL", "string": "Real Brasileiro", "saldo": "0.00000000"},
    {"codigo": "BTC", "string": "Bitcoin", "saldo": "0.00000000"},
    {"codigo": "ETH", "string": "Ethereum", "saldo": "0.00000000"},
    {"codigo": "SOL", "string": "Solana", "saldo": "0.00000000"},
    {"codigo": "USD", "string": "Dólar Americano", "saldo": "0.00000000"}
  ]
}
```

---

### 5. Realizar um Depósito

Vamos depositar 1000 BRL na carteira.

```bash
curl -X POST http://127.0.0.1:8000/carteiras/{endereco_carteira}/depositos \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_moeda": "BRL",
    "valor": 1000.00
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": true,
  "mensagem": "Depósito de 1000.0 BRL realizado com sucesso",
  "dados": {
    "endereco_carteira": "a1b2c3d4e5f6...",
    "codigo_moeda": "BRL",
    "valor": 1000.0
  }
}
```

---

### 6. Realizar um Saque

Vamos sacar 100 BRL. **Atenção:** Esta operação exige a chave privada!

```bash
curl -X POST http://127.0.0.1:8000/carteiras/{endereco_carteira}/saques \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_moeda": "BRL",
    "valor": 100.00,
    "chave_privada": "sua_chave_privada_aqui"
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": true,
  "mensagem": "Saque de 100.0 BRL realizado com sucesso",
  "dados": {
    "endereco_carteira": "a1b2c3d4e5f6...",
    "codigo_moeda": "BRL",
    "valor": 100.0
  }
}
```

**Nota:** Será cobrada uma taxa de 1% (configurada no .env), então o saldo será reduzido em 101 BRL.

---

### 7. Realizar uma Conversão de Moeda

Vamos converter 500 BRL para USD. **Atenção:** Esta operação exige a chave privada e usa a cotação real da Coinbase!

```bash
curl -X POST http://127.0.0.1:8000/carteiras/{endereco_carteira}/conversoes \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_origem": "BRL",
    "codigo_destino": "USD",
    "valor": 500.00,
    "chave_privada": "sua_chave_privada_aqui"
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": true,
  "mensagem": "Conversão de BRL para USD realizada com sucesso",
  "dados": {
    "valor_origem": 500.0,
    "moeda_origem": "BRL",
    "valor_destino": 95.5,
    "moeda_destino": "USD",
    "cotacao": 0.19,
    "taxa_percentual": 0.02,
    "taxa_valor": 1.91
  }
}
```

**Nota:** A cotação varia em tempo real. Será cobrada uma taxa de 2% sobre o valor convertido.

---

### 8. Realizar uma Transferência entre Carteiras

Primeiro, crie uma segunda carteira (repita o passo 2). Depois, transfira 50 USD da primeira para a segunda.

```bash
curl -X POST http://127.0.0.1:8000/carteiras/{endereco_origem}/transferencias \
  -H "Content-Type: application/json" \
  -d '{
    "endereco_destino": "endereco_da_segunda_carteira",
    "codigo_moeda": "USD",
    "valor": 50.00,
    "chave_privada": "chave_privada_da_carteira_origem"
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": true,
  "mensagem": "Transferência de 50.0 USD realizada com sucesso",
  "dados": {
    "endereco_origem": "a1b2c3d4e5f6...",
    "endereco_destino": "x9y8z7w6v5u4...",
    "codigo_moeda": "USD",
    "valor": 50.0
  }
}
```

**Nota:** A carteira de origem pagará uma taxa de 1% (0.50 USD), então será debitado 50.50 USD. A carteira de destino receberá exatamente 50 USD.

---

## Fluxo de Teste Completo

Para testar todas as funcionalidades em sequência:

1. **Criar Carteira A** → Anote o endereço e chave privada
2. **Criar Carteira B** → Anote o endereço e chave privada
3. **Depositar 1000 BRL na Carteira A**
4. **Consultar saldos da Carteira A** → Deve mostrar 1000 BRL
5. **Sacar 100 BRL da Carteira A** → Saldo fica em 899 BRL (taxa de 1%)
6. **Converter 500 BRL para USD na Carteira A** → Agora tem ~399 BRL e ~95 USD
7. **Transferir 50 USD da Carteira A para Carteira B** → A fica com ~44.5 USD, B recebe 50 USD
8. **Consultar saldos de ambas as carteiras** → Verificar se os valores estão corretos

---

## Tratamento de Erros

A API retorna mensagens de erro claras quando algo dá errado:

### Exemplo: Chave privada inválida

```json
{
  "detail": "Chave privada inválida"
}
```

### Exemplo: Saldo insuficiente

```json
{
  "detail": "Saldo insuficiente. Necessário: 101.00, Disponível: 50.00"
}
```

### Exemplo: Carteira não encontrada

```json
{
  "detail": "Carteira não encontrada"
}
```

### Exemplo: Moeda não encontrada

```json
{
  "detail": "Moeda BTC não encontrada"
}
```

---

## Dicas de Teste

- Use a interface Swagger (`/docs`) para testes rápidos e interativos.
- Salve sempre a chave privada ao criar uma carteira - ela não pode ser recuperada depois!
- Lembre-se das taxas: 1% para saques e transferências, 2% para conversões.
- As conversões usam cotações reais da Coinbase, então os valores podem variar.
- Sempre consulte os saldos antes e depois de cada operação para verificar a consistência.
- Use os códigos corretos das moedas: BTC, ETH, SOL, USD, BRL (sempre em maiúsculas).
