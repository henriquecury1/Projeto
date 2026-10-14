import csv
import sqlite3
from pathlib import Path

pasta = Path(__file__).parent
conexao = sqlite3.connect(pasta/"votacao.db")

with open(pasta / "eleitores.csv", encoding="utf-8-sig", newLine="") as arquivo: #csv pode não estar nessa
    leitor = csv.reader(arquivo, delimiter=",") #ver como as colunas estão separadas
    next(leitor)
    linhas = [linha for linha in leitor]

conexao.executemany(
    "INSERT OR REPLACE INTO eleitores (matricula, nome, cargo, setor) VALUES (?,?,?,?)",
    linhas,
)
conexao.commit()

total = conexao.execute("SELECT COUNT(*) FROM eleitores").fetchone()[0]
print(f"{total} eleitores importados")
conexao.close()
