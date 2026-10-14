CREATE TABLE eleitores(
    matricula TEXT PRIMARY KEY,
    nome TEXT,
    cargo TEXT,
    setor TEXT
);

CREATE TABLE candidatos(
    numero INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    cargo TEXT
);

CREATE TABLE participacao(
    matricula TEXT PRIMARY KEY REFERENCES eleitores(matricula)
);

CREATE TABLE votos(
    id TEXT PRIMARY KEY,
    candidato_numero INTEGER NULL,
    tipo TEXT CHECK (tipo IN ('valido','branco','nulo'))
);
