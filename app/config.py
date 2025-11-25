"""
Módulo de Configuração
Carrega as variáveis de ambiente do arquivo .env
"""
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Configurações do Banco de Dados
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'wallet_api_homolog')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'api123')
DB_NAME = os.getenv('DB_NAME', 'wallet_homolog')

# Configurações de Taxas
TAXA_SAQUE_PERCENTUAL = float(os.getenv('TAXA_SAQUE_PERCENTUAL', 0.01))
TAXA_CONVERSAO_PERCENTUAL = float(os.getenv('TAXA_CONVERSAO_PERCENTUAL', 0.02))
TAXA_TRANSFERENCIA_PERCENTUAL = float(os.getenv('TAXA_TRANSFERENCIA_PERCENTUAL', 0.01))

# Configurações de Chaves
PRIVATE_KEY_SIZE = int(os.getenv('PRIVATE_KEY_SIZE', 32))
PUBLIC_KEY_SIZE = int(os.getenv('PUBLIC_KEY_SIZE', 16))
