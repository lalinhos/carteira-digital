CREATE USER IF NOT EXISTS 'wallet_api_homolog'@'%'
    IDENTIFIED BY 'api123';
    
GRANT SELECT, INSERT, UPDATE, DELETE
    ON wallet_homolog.*
    TO 'wallet_api_homolog'@'%';

FLUSH PRIVILEGES;
USE wallet_homolog;
