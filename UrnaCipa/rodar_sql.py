import sqlite3
import sys
from pathlib import Path

pasta = Path(__file__).parent

if len(sys.argv) < 2:
    print("Uso: python rodar_sql.py arquivo.sql")
    sys.exit(1)

arquivo = pasta / sys.argv[1]
sql = arquivo.read_text(encoding = "utf-8")

conexao = sqlite3.connect(pasta/"votacao.db")
conexao.executescript(sql)
conexao.commit()
conexao.close()

print(f"{arquivo.name} executado com sucesso")
