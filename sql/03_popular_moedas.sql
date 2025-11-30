USE wallet_homolog;

-- insere as moedas
INSERT INTO MOEDA (codigo, string, tipo) VALUES
('BTC', 'Bitcoin', 'CRYPTO'),
('ETH', 'Ethereum', 'CRYPTO'),
('SOL', 'Solana', 'CRYPTO'),
('USD', 'Dólar Americano', 'FIAT'),
('BRL', 'Real Brasileiro', 'FIAT');