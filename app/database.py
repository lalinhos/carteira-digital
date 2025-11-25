"""
Módulo de Conexão com Banco de Dados
Gerencia a conexão com o MySQL usando SQL puro
"""
import pymysql
from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def get_connection():
    """
    Cria e retorna uma conexão com o banco de dados MySQL
    """
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    return connection


def execute_query(query, params=None, fetch=True):
    """
    Executa uma query SQL e retorna os resultados
    
    Args:
        query: String SQL a ser executada
        params: Tupla ou dicionário com os parâmetros da query
        fetch: Se True, retorna os resultados (SELECT). Se False, apenas executa (INSERT/UPDATE/DELETE)
    
    Returns:
        Lista de dicionários com os resultados (se fetch=True) ou None
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.lastrowid
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()


def execute_transaction(queries_with_params):
    """
    Executa múltiplas queries em uma transação
    
    Args:
        queries_with_params: Lista de tuplas (query, params)
    
    Returns:
        True se sucesso, levanta exceção se falhar
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            for query, params in queries_with_params:
                cursor.execute(query, params)
            connection.commit()
            return True
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()
