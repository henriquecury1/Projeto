import sqlite3
from pathlib import Path

pasta = Path(__file__).parent

conexao = sqlite3.connect(pasta/"votacao.db")
sql = (pasta / "schema.sql").read_text(encoding = "utf-8")
conexao.executescript(sql)
conexao.commit()
conexao.close()

print("Banco criado com sucesso")
