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
    
    # inserir carteira no banco
    query = """
        INSERT INTO CARTEIRA (endereco_carteira, hash_chave_privada, status)
        VALUES (%s, %s, 'ATIVA')
    """
    execute_query(query, (endereco_carteira, hash_chave), fetch=False)
    
    # iniciliza saldos zerados para todas as moedas
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

# consulta a carteira
def obter_carteira(endereco_carteira):
    query = """
        SELECT endereco_carteira, data_criacao, status
        FROM CARTEIRA
        WHERE endereco_carteira = %s
    """
    resultado = execute_query(query, (endereco_carteira,))
    
    if resultado:
        return resultado[0]
    return None

# consulta o saldo da carteira
def obter_saldos(endereco_carteira):
    query = """
        SELECT m.codigo, m.string, sc.saldo
        FROM SALDO_CARTEIRA sc
        JOIN MOEDA m ON sc.id_moeda = m.id_moeda
        WHERE sc.endereco_carteira = %s
        ORDER BY m.codigo
    """
    return execute_query(query, (endereco_carteira,))

# consulta o código da moeda
def obter_id_moeda(codigo):
    query = """
        SELECT id_moeda
        FROM MOEDA
        WHERE codigo = %s
    """
    resultado = execute_query(query, (codigo,))
    
    if resultado:
        return resultado[0]['id_moeda']
    return None

# consulta o saldo da carteira 
def obter_saldo_moeda(endereco_carteira, codigo_moeda):
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

# consulta a chave privada pelo endereço da carteira
def verificar_chave_privada(endereco_carteira, chave_privada):
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
    # obter id_moeda, chama a função
    id_moeda = obter_id_moeda(codigo_moeda)
    if not id_moeda:
        raise ValueError(f"Moeda {codigo_moeda} não encontrada")
    
    queries = [
        # insere o depósito na carteira
        ("""
            INSERT INTO DEPOSITO_SAQUE (endereco_carteira, id_moeda, valor, tipo, taxa_valor)
            VALUES (%s, %s, %s, 'DEPOSITO', 0.00000000)
        """, (endereco_carteira, id_moeda, valor)),
        
        # faz um update e atualiza para o novo saldo
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
    # validar chave privada
    if not verificar_chave_privada(endereco_carteira, chave_privada):
        raise ValueError("Chave privada inválida")
    
    # obter id_moeda
    id_moeda = obter_id_moeda(codigo_moeda)
    if not id_moeda:
        raise ValueError(f"Moeda {codigo_moeda} não encontrada")
    
    # calcular taxa
    taxa_valor = Decimal(str(valor)) * Decimal(str(TAXA_SAQUE_PERCENTUAL))
    valor_total = Decimal(str(valor)) + taxa_valor
    
    # verificar saldo
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
    url = f"https://api.coinbase.com/v2/prices/{codigo_origem}-{codigo_destino}/spot" # utilizando API da coinbase para cotação
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        cotacao = Decimal(data['data']['amount'])
        return cotacao
    except Exception as e:
        raise ValueError(f"Erro ao obter cotação: {str(e)}")


def realizar_conversao(endereco_carteira, codigo_origem, codigo_destino, valor, chave_privada):
    # chama a função de verificação de chave privada para ver se ela existe
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
