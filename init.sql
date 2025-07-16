-- Criação da tabela de filmes
CREATE TABLE filmes (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    imagem_url TEXT,
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de avaliações
CREATE TABLE avaliacoes (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    roteiro INT CHECK (roteiro BETWEEN 1 AND 5),
    atuacao INT CHECK (atuacao BETWEEN 1 AND 5),
    direcao INT CHECK (direcao BETWEEN 1 AND 5),
    fotografia INT CHECK (fotografia BETWEEN 1 AND 5),
    trilha INT CHECK (trilha BETWEEN 1 AND 5),
    montagem INT CHECK (montagem BETWEEN 1 AND 5),
    impacto INT CHECK (impacto BETWEEN 1 AND 5),
    critica TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filme_id INT NOT NULL REFERENCES filmes(id),
    total INT CHECK (total BETWEEN 1 AND 10)
);

-- Tabela de configurações
CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    filme_da_semana_id INT REFERENCES filmes(id),
    senha_config TEXT NOT NULL
);
