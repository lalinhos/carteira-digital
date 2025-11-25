"""
Módulo de Utilitários
Funções auxiliares para geração de chaves, hash e validações
"""
import secrets
import hashlib
from app.config import PRIVATE_KEY_SIZE, PUBLIC_KEY_SIZE


def gerar_chave_publica():
    """
    Gera uma chave pública (endereço da carteira) aleatória
    
    Returns:
        String hexadecimal representando o endereço da carteira
    """
    return secrets.token_hex(PUBLIC_KEY_SIZE)


def gerar_chave_privada():
    """
    Gera uma chave privada aleatória
    
    Returns:
        String hexadecimal representando a chave privada
    """
    return secrets.token_hex(PRIVATE_KEY_SIZE)


def hash_chave_privada(chave_privada):
    """
    Gera o hash SHA-256 de uma chave privada
    
    Args:
        chave_privada: String da chave privada
    
    Returns:
        String hexadecimal do hash SHA-256
    """
    return hashlib.sha256(chave_privada.encode()).hexdigest()


def validar_chave_privada(chave_privada, hash_armazenado):
    """
    Valida se uma chave privada corresponde ao hash armazenado
    
    Args:
        chave_privada: String da chave privada fornecida
        hash_armazenado: Hash armazenado no banco de dados
    
    Returns:
        True se a chave é válida, False caso contrário
    """
    return hash_chave_privada(chave_privada) == hash_armazenado
