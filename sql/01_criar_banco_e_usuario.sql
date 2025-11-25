-- Criar o banco de dados
CREATE DATABASE IF NOT EXISTS wallet_homolog;

-- Criar o usuário da API
CREATE USER IF NOT EXISTS 'wallet_api_homolog'@'localhost' IDENTIFIED BY 'api123';

-- Conceder permissões DML (apenas SELECT, INSERT, UPDATE, DELETE)
GRANT SELECT, INSERT, UPDATE, DELETE ON wallet_homolog.* TO 'wallet_api_homolog'@'localhost';

-- Aplicar as mudanças
FLUSH PRIVILEGES;

