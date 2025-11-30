"""
Define os modelos Pydantic para validação de entrada e saída da API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# Modelos de Resposta
class CarteiraResponse(BaseModel):
    endereco_carteira: str
    chave_privada: Optional[str] = None  # Apenas na criação
    data_criacao: Optional[datetime] = None
    status: Optional[str] = None


class SaldoMoedaResponse(BaseModel):
    codigo: str
    string: str
    saldo: Decimal

class SaldosResponse(BaseModel):
    endereco_carteira: str
    saldos: list[SaldoMoedaResponse]


# Modelos de Requisição
class DepositoRequest(BaseModel):
    codigo_moeda: str = Field(..., description="Código da moeda (BTC, ETH, SOL, USD, BRL)")
    valor: Decimal = Field(..., gt=0, description="Valor do depósito (deve ser maior que 0)")


class SaqueRequest(BaseModel):
    codigo_moeda: str = Field(..., description="Código da moeda (BTC, ETH, SOL, USD, BRL)")
    valor: Decimal = Field(..., gt=0, description="Valor do saque (deve ser maior que 0)")
    chave_privada: str = Field(..., description="Chave privada para autenticação")


class ConversaoRequest(BaseModel):
    codigo_origem: str = Field(..., description="Código da moeda de origem")
    codigo_destino: str = Field(..., description="Código da moeda de destino")
    valor: Decimal = Field(..., gt=0, description="Valor a ser convertido")
    chave_privada: str = Field(..., description="Chave privada para autenticação")


class TransferenciaRequest(BaseModel):
    endereco_destino: str = Field(..., description="Endereço da carteira de destino")
    codigo_moeda: str = Field(..., description="Código da moeda")
    valor: Decimal = Field(..., gt=0, description="Valor a ser transferido")
    chave_privada: str = Field(..., description="Chave privada para autenticação")


# Modelos de Resposta de Operações
class OperacaoResponse(BaseModel):
    sucesso: bool
    mensagem: str
    dados: Optional[dict] = None
