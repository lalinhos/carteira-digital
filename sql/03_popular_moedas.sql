USE wallet_homolog;

-- Inserir as moedas
INSERT INTO MOEDA (codigo, string, tipo) VALUES
('BTC', 'Bitcoin', 'CRYPTO'),
('ETH', 'Ethereum', 'CRYPTO'),
('SOL', 'Solana', 'CRYPTO'),
('USD', 'Dólar Americano', 'FIAT'),
('BRL', 'Real Brasileiro', 'FIAT');