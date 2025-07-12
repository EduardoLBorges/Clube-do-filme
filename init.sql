CREATE TABLE filmes (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    imagem_url TEXT,
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE avaliacoes (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    roteiro INT,
    atuacao INT,
    direcao INT,
    fotografia INT,
    trilha INT,
    montagem INT,
    impacto INT,
    critica TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filme_id INT REFERENCES filmes(id)
);
