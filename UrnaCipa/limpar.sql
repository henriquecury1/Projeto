DELETE FROM participacao;
DELETE FROM votos;
UPDATE eleicao SET status = 'encerrada' WHERE id = 1;
