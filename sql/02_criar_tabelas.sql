CREATE TABLE IF NOT EXISTS MOEDA (
    id_moeda SMALLINT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    string VARCHAR(50) NOT NULL,
    tipo ENUM('CRYPTO', 'FIAT') NOT NULL
);

CREATE TABLE IF NOT EXISTS CARTEIRA (
    endereco_carteira VARCHAR(64) PRIMARY KEY,
    hash_chave_privada VARCHAR(128) NOT NULL,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ATIVA', 'BLOQUEADA') NOT NULL DEFAULT 'ATIVA'
);

CREATE TABLE IF NOT EXISTS SALDO_CARTEIRA (
    endereco_carteira VARCHAR(64) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    saldo DECIMAL(20, 8) NOT NULL DEFAULT 0.00000000,
    
    PRIMARY KEY (endereco_carteira, id_moeda),
    
    FOREIGN KEY (endereco_carteira) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES MOEDA(id_moeda)
);

CREATE TABLE IF NOT EXISTS DEPOSITO_SAQUE (
    id_movimento INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(64) NOT NULL,
    
    id_moeda SMALLINT NOT NULL, 
    
    valor DECIMAL(20, 8) NOT NULL,
    tipo ENUM('DEPOSITO', 'SAQUE') NOT NULL,
    taxa_valor DECIMAL(20, 8) DEFAULT 0.00000000,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (endereco_carteira) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES MOEDA(id_moeda)
);

CREATE TABLE IF NOT EXISTS CONVERSAO (
    id_conversao BIGINT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(64) NOT NULL,
    id_moeda_origem smallint(10) NOT NULL,
    id_moeda_destino smallint(10) NOT NULL,
    valor_origem DECIMAL(20, 8) NOT NULL,
    valor_destino DECIMAL(20, 8) NOT NULL,
    taxa_percentual DECIMAL(5, 4) NOT NULL,
    taxa_valor DECIMAL(20, 8) NOT NULL DEFAULT 0.00000000,
    cotacao_utilizada DECIMAL(20, 8) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (endereco_carteira) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (id_moeda_origem) REFERENCES MOEDA(id_moeda),
    FOREIGN KEY (id_moeda_destino) REFERENCES MOEDA(id_moeda)
);

CREATE TABLE IF NOT EXISTS TRANSFERENCIA (
    id_transferencia INT AUTO_INCREMENT PRIMARY KEY,
    endereco_origem VARCHAR(64) NOT NULL,
    endereco_destino VARCHAR(64) NOT NULL,
    
    id_moeda SMALLINT NOT NULL,
    
    valor DECIMAL(20, 8) NOT NULL,
    taxa_valor DECIMAL(20, 8) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (endereco_origem) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (endereco_destino) REFERENCES CARTEIRA(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES MOEDA(id_moeda)
);