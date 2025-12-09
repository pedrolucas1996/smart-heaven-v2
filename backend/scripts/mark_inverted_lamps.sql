-- Mark lamps that have inverted hardware signals
-- Based on user report: L_quarto is inverted, L_escritorio is normal

-- Update L_Quarto as inverted
UPDATE lampada SET invertido = 1 WHERE nome = 'L_Quarto';

-- Query to see all lamps and their current inversion status
SELECT 
    id,
    nome,
    base_id,
    estado,
    invertido,
    data_de_atualizacao
FROM lampada
ORDER BY nome;

-- Note: Test each lamp physically to identify other inverted lamps
-- Lamps that turn OFF when command says ON need invertido = 1
