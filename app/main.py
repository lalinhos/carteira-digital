from fastapi import FastAPI, HTTPException, status
from app.models import (
    CarteiraResponse, SaldosResponse, OperacaoResponse,
    DepositoRequest, SaqueRequest, ConversaoRequest, TransferenciaRequest
)
from app.services import (
    criar_carteira, obter_carteira, obter_saldos,
    realizar_deposito, realizar_saque, realizar_conversao, realizar_transferencia
)

# cria aplicação FastAPI
app = FastAPI(
    title="Carteira Digital API",
    description="API para gerenciamento de carteiras digitais com suporte a múltiplas moedas",
    version="1.0.0"
)


# post para criar uma nova carteira
# retorna o endereço da carteira e a chave privada
@app.post("/carteiras", response_model=CarteiraResponse, status_code=status.HTTP_201_CREATED)
def criar_nova_carteira():
    try:
        resultado = criar_carteira()
        return CarteiraResponse(
            endereco_carteira=resultado['endereco_carteira'],
            chave_privada=resultado['chave_privada']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar carteira: {str(e)}"
        )

# get para consultar informações de uma carteira (endereço, data de criação e status)
@app.get("/carteiras/{endereco_carteira}", response_model=CarteiraResponse)
def consultar_carteira(endereco_carteira: str):
    carteira = obter_carteira(endereco_carteira)
    
    if not carteira:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira não encontrada"
        )
    
    return CarteiraResponse(
        endereco_carteira=carteira['endereco_carteira'],
        data_criacao=carteira['data_criacao'],
        status=carteira['status']
    )

# consulta o saldo e retorna lista com o saldo de cada moeda
@app.get("/carteiras/{endereco_carteira}/saldos", response_model=SaldosResponse)
def consultar_saldos(endereco_carteira: str):
    # verifica se carteira existe
    carteira = obter_carteira(endereco_carteira)
    if not carteira:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira não encontrada"
        )
    
    saldos = obter_saldos(endereco_carteira)
    
    return SaldosResponse(
        endereco_carteira=endereco_carteira,
        saldos=saldos
    )


# ENDPOINTS DE DEPÓSITOS
# realiza depósito de um tipo de moeda
@app.post("/carteiras/{endereco_carteira}/depositos", response_model=OperacaoResponse)
def depositar(endereco_carteira: str, deposito: DepositoRequest):
    # Verificar se carteira existe
    carteira = obter_carteira(endereco_carteira)
    if not carteira:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira não encontrada"
        )
    
    try:
        realizar_deposito(endereco_carteira, deposito.codigo_moeda, deposito.valor)
        
        return OperacaoResponse(
            sucesso=True,
            mensagem=f"Depósito de {deposito.valor} {deposito.codigo_moeda} realizado com sucesso",
            dados={
                "endereco_carteira": endereco_carteira,
                "codigo_moeda": deposito.codigo_moeda,
                "valor": float(deposito.valor)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao realizar depósito: {str(e)}"
        )


# ENDPOINTS DE SAQUES

@app.post("/carteiras/{endereco_carteira}/saques", response_model=OperacaoResponse)
def sacar(endereco_carteira: str, saque: SaqueRequest):
    """
    Realiza um saque de uma moeda específica
    
    Exige autenticação por chave privada e cobra taxa
    """
    # Verificar se carteira existe
    carteira = obter_carteira(endereco_carteira)
    if not carteira:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira não encontrada"
        )
    
    try:
        realizar_saque(endereco_carteira, saque.codigo_moeda, saque.valor, saque.chave_privada)
        
        return OperacaoResponse(
            sucesso=True,
            mensagem=f"Saque de {saque.valor} {saque.codigo_moeda} realizado com sucesso",
            dados={
                "endereco_carteira": endereco_carteira,
                "codigo_moeda": saque.codigo_moeda,
                "valor": float(saque.valor)
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar saque: {str(e)}"
        )


# ENDPOINTS DE CONVERSÃO

@app.post("/carteiras/{endereco_carteira}/conversoes", response_model=OperacaoResponse)
def converter_moeda(endereco_carteira: str, conversao: ConversaoRequest):
    """
    Realiza conversão entre duas moedas
    
    Usa cotação da API da Coinbase, exige autenticação e cobra taxa
    """
    # Verificar se carteira existe
    carteira = obter_carteira(endereco_carteira)
    if not carteira:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira não encontrada"
        )
    
    try:
        resultado = realizar_conversao(
            endereco_carteira,
            conversao.codigo_origem,
            conversao.codigo_destino,
            conversao.valor,
            conversao.chave_privada
        )
        
        return OperacaoResponse(
            sucesso=True,
            mensagem=f"Conversão de {conversao.codigo_origem} para {conversao.codigo_destino} realizada com sucesso",
            dados=resultado
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar conversão: {str(e)}"
        )


# ENDPOINTS DE TRANSFERÊNCIA

@app.post("/carteiras/{endereco_origem}/transferencias", response_model=OperacaoResponse)
def transferir(endereco_origem: str, transferencia: TransferenciaRequest):
    """
    Realiza transferência de valor entre carteiras
    
    Exige autenticação da carteira de origem e cobra taxa
    """
    # Verificar se carteira origem existe
    carteira_origem = obter_carteira(endereco_origem)
    if not carteira_origem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira de origem não encontrada"
        )
    
    try:
        realizar_transferencia(
            endereco_origem,
            transferencia.endereco_destino,
            transferencia.codigo_moeda,
            transferencia.valor,
            transferencia.chave_privada
        )
        
        return OperacaoResponse(
            sucesso=True,
            mensagem=f"Transferência de {transferencia.valor} {transferencia.codigo_moeda} realizada com sucesso",
            dados={
                "endereco_origem": endereco_origem,
                "endereco_destino": transferencia.endereco_destino,
                "codigo_moeda": transferencia.codigo_moeda,
                "valor": float(transferencia.valor)
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar transferência: {str(e)}"
        )


# ENDPOINT DE SAÚDE

@app.get("/")
def root():
    
    return {
        "mensagem": "API de Carteira Digital está funcionando!",
        "versao": "1.0.0",
        "documentacao": "/docs"
    }


@app.get("/health")
def health_check():
    """
    Endpoint de health check
    """
    return {"status": "healthy"}
