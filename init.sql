CREATE TABLE avaliacoes (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    roteiro INTEGER,
    atuacao INTEGER,
    direcao INTEGER,
    fotografia INTEGER,
    trilha INTEGER,
    montagem INTEGER,
    impacto INTEGER,
    critica TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
