import csv
import sqlite3
from pathlib import Path

pasta = Path(__file__).parent
conexao = sqlite3.connect(pasta/"votacao.db")

with open(pasta / "eleitores.csv", encoding="cp850", newline="") as arquivo: #csv pode não estar nessa
    leitor = csv.reader(arquivo, delimiter=";") #ver como as colunas estão separadas
    next(leitor)
    linhas = [[campo.strip() for campo in linha] for linha in leitor if linha]

conexao.executemany(
    "INSERT OR REPLACE INTO eleitores (matricula, nome, cargo, setor) VALUES (?,?,?,?)",
    linhas,
)
conexao.commit()

total = conexao.execute("SELECT COUNT(*) FROM eleitores").fetchone()[0]
print(f"{total} eleitores importados")
conexao.close()
