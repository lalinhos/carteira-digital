"""
Contém a lógica de negócio para todas as operações da carteira
"""
from decimal import Decimal
from app.database import execute_query, execute_transaction
from app.utils import gerar_chave_publica, gerar_chave_privada, hash_chave_privada, validar_chave_privada
from app.config import TAXA_SAQUE_PERCENTUAL, TAXA_CONVERSAO_PERCENTUAL, TAXA_TRANSFERENCIA_PERCENTUAL
import requests

# CARTEIRAS 

def criar_carteira():
    """
    Cria uma nova carteira com chave pública e privada
    
    Returns:
        Dicionário com endereco_carteira e chave_privada
    """
    endereco_carteira = gerar_chave_publica()
    chave_privada = gerar_chave_privada()
    hash_chave = hash_chave_privada(chave_privada)
    
    # Inserir carteira no banco
    query = """
        INSERT INTO CARTEIRA (endereco_carteira, hash_chave_privada, status)
        VALUES (%s, %s, 'ATIVA')
    """
    execute_query(query, (endereco_carteira, hash_chave), fetch=False)
    
    # Inicializar saldos zerados para todas as moedas
    moedas = execute_query("SELECT id_moeda FROM MOEDA")
    for moeda in moedas:
        query_saldo = """
            INSERT INTO SALDO_CARTEIRA (endereco_carteira, id_moeda, saldo)
            VALUES (%s, %s, 0.00000000)
        """
        execute_query(query_saldo, (endereco_carteira, moeda['id_moeda']), fetch=False)
    
    return {
        'endereco_carteira': endereco_carteira,
        'chave_privada': chave_privada
    }


def obter_carteira(endereco_carteira):
    """
    Obtém informações básicas de uma carteira
    
    Args:
        endereco_carteira: Endereço da carteira
    
    Returns:
        Dicionário com informações da carteira ou None
    """
    query = """
        SELECT endereco_carteira, data_criacao, status
        FROM CARTEIRA
        WHERE endereco_carteira = %s
    """
    resultado = execute_query(query, (endereco_carteira,))
    
    if resultado:
        return resultado[0]
    return None


def obter_saldos(endereco_carteira):
    """
    Obtém os saldos de todas as moedas de uma carteira
    
    Args:
        endereco_carteira: Endereço da carteira
    
    Returns:
        Lista de dicionários com codigo, string e saldo
    """
    query = """
        SELECT m.codigo, m.string, sc.saldo
        FROM SALDO_CARTEIRA sc
        JOIN MOEDA m ON sc.id_moeda = m.id_moeda
        WHERE sc.endereco_carteira = %s
        ORDER BY m.codigo
    """
    return execute_query(query, (endereco_carteira,))


def obter_id_moeda(codigo):
    """
    Obtém o id_moeda a partir do código da moeda
    
    Args:
        codigo: Código da moeda (BTC, ETH, etc.)
    
    Returns:
        id_moeda ou None
    """
    query = """
        SELECT id_moeda
        FROM MOEDA
        WHERE codigo = %s
    """
    resultado = execute_query(query, (codigo,))
    
    if resultado:
        return resultado[0]['id_moeda']
    return None


def obter_saldo_moeda(endereco_carteira, codigo_moeda):
    """
    Obtém o saldo de uma moeda específica
    
    Args:
        endereco_carteira: Endereço da carteira
        codigo_moeda: Código da moeda (BTC, ETH, etc.)
    
    Returns:
        Decimal com o saldo ou None
    """
    query = """
        SELECT sc.saldo
        FROM SALDO_CARTEIRA sc
        JOIN MOEDA m ON sc.id_moeda = m.id_moeda
        WHERE sc.endereco_carteira = %s AND m.codigo = %s
    """
    resultado = execute_query(query, (endereco_carteira, codigo_moeda))
    
    if resultado:
        return Decimal(str(resultado[0]['saldo']))
    return None


def verificar_chave_privada(endereco_carteira, chave_privada):
    """
    Verifica se a chave privada corresponde à carteira
    
    Args:
        endereco_carteira: Endereço da carteira
        chave_privada: Chave privada fornecida
    
    Returns:
        True se válida, False caso contrário
    """
    query = """
        SELECT hash_chave_privada
        FROM CARTEIRA
        WHERE endereco_carteira = %s
    """
    resultado = execute_query(query, (endereco_carteira,))
    
    if resultado:
        hash_armazenado = resultado[0]['hash_chave_privada']
        return validar_chave_privada(chave_privada, hash_armazenado)
    return False


# DEPÓSITOS

def realizar_deposito(endereco_carteira, codigo_moeda, valor):
    """
    Realiza um depósito na carteira
    
    Args:
        endereco_carteira: Endereço da carteira
        codigo_moeda: Código da moeda (BTC, ETH, etc.)
        valor: Valor do depósito
    
    Returns:
        True se sucesso
    """
    # Obter id_moeda
    id_moeda = obter_id_moeda(codigo_moeda)
    if not id_moeda:
        raise ValueError(f"Moeda {codigo_moeda} não encontrada")
    
    queries = [
        # Registrar o depósito
        ("""
            INSERT INTO DEPOSITO_SAQUE (endereco_carteira, id_moeda, valor, tipo, taxa_valor)
            VALUES (%s, %s, %s, 'DEPOSITO', 0.00000000)
        """, (endereco_carteira, id_moeda, valor)),
        
        # Atualizar saldo
        ("""
            UPDATE SALDO_CARTEIRA
            SET saldo = saldo + %s
            WHERE endereco_carteira = %s AND id_moeda = %s
        """, (valor, endereco_carteira, id_moeda))
    ]
    
    execute_transaction(queries)
    return True


# SAQUES

def realizar_saque(endereco_carteira, codigo_moeda, valor, chave_privada):
    """
    Realiza um saque da carteira
    
    Args:
        endereco_carteira: Endereço da carteira
        codigo_moeda: Código da moeda (BTC, ETH, etc.)
        valor: Valor do saque
        chave_privada: Chave privada para autenticação
    
    Returns:
        True se sucesso, levanta exceção se falhar
    """
    # Validar chave privada
    if not verificar_chave_privada(endereco_carteira, chave_privada):
        raise ValueError("Chave privada inválida")
    
    # Obter id_moeda
    id_moeda = obter_id_moeda(codigo_moeda)
    if not id_moeda:
        raise ValueError(f"Moeda {codigo_moeda} não encontrada")
    
    # Calcular taxa
    taxa_valor = Decimal(str(valor)) * Decimal(str(TAXA_SAQUE_PERCENTUAL))
    valor_total = Decimal(str(valor)) + taxa_valor
    
    # Verificar saldo
    saldo_atual = obter_saldo_moeda(endereco_carteira, codigo_moeda)
    if saldo_atual is None or saldo_atual < valor_total:
        raise ValueError(f"Saldo insuficiente. Necessário: {valor_total}, Disponível: {saldo_atual}")
    
    queries = [
        # Registrar o saque
        ("""
            INSERT INTO DEPOSITO_SAQUE (endereco_carteira, id_moeda, valor, tipo, taxa_valor)
            VALUES (%s, %s, %s, 'SAQUE', %s)
        """, (endereco_carteira, id_moeda, valor, taxa_valor)),
        
        # Atualizar saldo (debitar valor + taxa)
        ("""
            UPDATE SALDO_CARTEIRA
            SET saldo = saldo - %s
            WHERE endereco_carteira = %s AND id_moeda = %s
        """, (valor_total, endereco_carteira, id_moeda))
    ]
    
    execute_transaction(queries)
    return True


# CONVERSÃO 

def obter_cotacao_coinbase(codigo_origem, codigo_destino):
    """
    Obtém a cotação de conversão da API da Coinbase
    
    Args:
        codigo_origem: Código da moeda de origem
        codigo_destino: Código da moeda de destino
    
    Returns:
        Decimal com a cotação
    """
    url = f"https://api.coinbase.com/v2/prices/{codigo_origem}-{codigo_destino}/spot"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        cotacao = Decimal(data['data']['amount'])
        return cotacao
    except Exception as e:
        raise ValueError(f"Erro ao obter cotação: {str(e)}")


def realizar_conversao(endereco_carteira, codigo_origem, codigo_destino, valor, chave_privada):
    """
    Realiza conversão entre moedas
    
    Args:
        endereco_carteira: Endereço da carteira
        codigo_origem: Código da moeda de origem
        codigo_destino: Código da moeda de destino
        valor: Valor a ser convertido
        chave_privada: Chave privada para autenticação
    
    Returns:
        Dicionário com detalhes da conversão
    """
    # Validar chave privada
    if not verificar_chave_privada(endereco_carteira, chave_privada):
        raise ValueError("Chave privada inválida")
    
    # Obter ids das moedas
    id_moeda_origem = obter_id_moeda(codigo_origem)
    id_moeda_destino = obter_id_moeda(codigo_destino)
    
    if not id_moeda_origem or not id_moeda_destino:
        raise ValueError("Moeda não encontrada")
    
    # Verificar saldo
    saldo_origem = obter_saldo_moeda(endereco_carteira, codigo_origem)
    if saldo_origem is None or saldo_origem < Decimal(str(valor)):
        raise ValueError(f"Saldo insuficiente na moeda de origem")
    
    # Obter cotação
    cotacao = obter_cotacao_coinbase(codigo_origem, codigo_destino)
    
    # Calcular valores
    valor_convertido_bruto = Decimal(str(valor)) * cotacao
    taxa_valor = valor_convertido_bruto * Decimal(str(TAXA_CONVERSAO_PERCENTUAL))
    valor_destino = valor_convertido_bruto - taxa_valor
    
    queries = [
        # Registrar conversão
        ("""
            INSERT INTO CONVERSAO (endereco_carteira, id_moeda_origem, id_moeda_destino, 
                                   valor_origem, valor_destino, taxa_percentual, taxa_valor, cotacao_utilizada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (endereco_carteira, id_moeda_origem, id_moeda_destino, valor, valor_destino, 
              TAXA_CONVERSAO_PERCENTUAL, taxa_valor, cotacao)),
        
        # Debitar moeda de origem
        ("""
            UPDATE SALDO_CARTEIRA
            SET saldo = saldo - %s
            WHERE endereco_carteira = %s AND id_moeda = %s
        """, (valor, endereco_carteira, id_moeda_origem)),
        
        # Creditar moeda de destino
        ("""
            UPDATE SALDO_CARTEIRA
            SET saldo = saldo + %s
            WHERE endereco_carteira = %s AND id_moeda = %s
        """, (valor_destino, endereco_carteira, id_moeda_destino))
    ]
    
    execute_transaction(queries)
    
    return {
        'valor_origem': float(valor),
        'moeda_origem': codigo_origem,
        'valor_destino': float(valor_destino),
        'moeda_destino': codigo_destino,
        'cotacao': float(cotacao),
        'taxa_percentual': float(TAXA_CONVERSAO_PERCENTUAL),
        'taxa_valor': float(taxa_valor)
    }


# TRANSFERÊNCIA

def realizar_transferencia(endereco_origem, endereco_destino, codigo_moeda, valor, chave_privada):
    """
    Realiza transferência entre carteiras
    
    Args:
        endereco_origem: Endereço da carteira de origem
        endereco_destino: Endereço da carteira de destino
        codigo_moeda: Código da moeda
        valor: Valor a ser transferido
        chave_privada: Chave privada da carteira de origem
    
    Returns:
        True se sucesso
    """
    # Validar chave privada
    if not verificar_chave_privada(endereco_origem, chave_privada):
        raise ValueError("Chave privada inválida")
    
    # Verificar se carteira destino existe
    carteira_destino = obter_carteira(endereco_destino)
    if not carteira_destino:
        raise ValueError("Carteira de destino não encontrada")
    
    # Obter id_moeda
    id_moeda = obter_id_moeda(codigo_moeda)
    if not id_moeda:
        raise ValueError(f"Moeda {codigo_moeda} não encontrada")
    
    # Calcular taxa
    taxa_valor = Decimal(str(valor)) * Decimal(str(TAXA_TRANSFERENCIA_PERCENTUAL))
    valor_total = Decimal(str(valor)) + taxa_valor
    
    # Verificar saldo
    saldo_origem = obter_saldo_moeda(endereco_origem, codigo_moeda)
    if saldo_origem is None or saldo_origem < valor_total:
        raise ValueError(f"Saldo insuficiente. Necessário: {valor_total}, Disponível: {saldo_origem}")
    
    queries = [
        # Registrar transferência
        ("""
            INSERT INTO TRANSFERENCIA (endereco_origem, endereco_destino, id_moeda, valor, taxa_valor)
            VALUES (%s, %s, %s, %s, %s)
        """, (endereco_origem, endereco_destino, id_moeda, valor, taxa_valor)),
        
        # Debitar origem (valor + taxa)
        ("""
            UPDATE SALDO_CARTEIRA
            SET saldo = saldo - %s
            WHERE endereco_carteira = %s AND id_moeda = %s
        """, (valor_total, endereco_origem, id_moeda)),
        
        # Creditar destino (apenas valor, sem taxa)
        ("""
            UPDATE SALDO_CARTEIRA
            SET saldo = saldo + %s
            WHERE endereco_carteira = %s AND id_moeda = %s
        """, (valor, endereco_destino, id_moeda))
    ]
    
    execute_transaction(queries)
    return True
