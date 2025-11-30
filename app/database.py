import pymysql
from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# conexão com o banco
def get_connection():
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

# função para executar uma query
def execute_query(query, params=None, fetch=True):
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

# função para executar mais de uma query
def execute_transaction(queries_with_params):
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
