import uuid
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PASTA = Path(__file__).parent
BANCO = PASTA/"votacao.db"
PORTA = 800

def consultar(sql, parametros=()):
    """Roda um SELECT e devolve a primeira linha(ou None)"""
    conexao = sqlite3.connect(BANCO)
    try:
        conexao.execute(sql, parametros).fetchone()
    finally:
        conexao.close()
#
class Urna(BaseHTTPRequestHandler): #Funcionaria como uma API

    def responder_json(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii = False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def enviar_arquivo(self, nome, tipo):
        corpo = (PASTA / nome).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        partes = self.path.strip("/").split("/") #"/api/eleitor/123"

        if self.path == "/":
            self.enviar_arquivo("index.html", "text/html; charset = utf-8")

        elif len(partes) == 3 and partes[:2] == ["api", "eleitor"]:
            self.buscar_eleitor(partes[2])

        elif len(partes) == 3 and partes[:2] == ["api", "candidato"]:
            self.buscar_candidato(partes[2])

        else:
            self.responder_json(403,{"erro": "Rota não encontrada"})

    def buscar_eleitor(self, matricula):
        linha = consultar(""""
            SELECT e.matricula, e.nome, e.cargo, e.setor,
                CASE WHEN p.matricula IS NULL THEN 1 ELSE 0 END
            FROM eleitores e
            LEFT JOIN participacao p ON p.matricula = e.matricula
            WHERE e.matricula = ?""", (matricula,))

        if linha is None:
            self.responder_json(403, {"erro": "Colaborador não encontrado"})
            return

        self.responder_json(200,{
            "matricula": linha[0],
            "nome": linha[1],
            "cargo": linha[2],
            "setor": linha[3],              
        })

        def buscar_candidato(self, numero):
            if not numero.isdigit():
                self.responder_json(400, {"erro": "Número inválido"})
                return

            linha = consultar(
                "SELECT numero, nome, cargo FROM candidatos WHERE numero = ?",
                (int(numero),))

            if linha is None:
                self.responder_json(404, {"erro": "Candidato não existe (voto nulo)"})
                return

            self.responder_json(200, {"numero": linha[0], "nome": linha[1], "cargo": linha[2]})

            def do_POST(self):
                if self.path == "/api/votar":
                    self.votar()
                else:
                    self.responder_json(404, {"erro": "Rota não encontrada"})

    def ler_json(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(tamanho) or b"{}")
        except json.JSONDecodeError:
            return None

    def votar(self):
        dados = self.ler_json()
        if not isinstance(dados, dict) or not dados.get("matricula"):
            self.responder_json(400, {"erro": "Pedido inválido"})
            return

        matricula = str(dados["matricula"])
        numero = dados.get("numero")          # None = voto em branco

        conexao = sqlite3.connect(BANCO)
        try:
            # 1. A votação está aberta?
            status = conexao.execute("SELECT status FROM eleicao WHERE id = 1").fetchone()[0]
            if status != "aberta":
                self.responder_json(403, {"erro": "A votação não está aberta"})
                return

            # 2. O eleitor existe?
            if conexao.execute("SELECT 1 FROM eleitores WHERE matricula = ?",
                               (matricula,)).fetchone() is None:
                self.responder_json(404, {"erro": "Colaborador não encontrado"})
                return

            # 3. Que tipo de voto é?
            if numero is None:
                tipo = "branco"
            elif str(numero).isdigit() and conexao.execute(
                    "SELECT 1 FROM candidatos WHERE numero = ?", (int(numero),)).fetchone():
                tipo, numero = "valido", int(numero)
            else:
                tipo, numero = "nulo", None

            # 4. Grava os dois registros numa única transação
            try:
                with conexao:
                    conexao.execute("INSERT INTO participacao (matricula) VALUES (?)",
                                    (matricula,))
                    conexao.execute(
                        "INSERT INTO votos (id, candidato_numero, tipo) VALUES (?, ?, ?)",
                        (str(uuid.uuid4()), numero, tipo))
            except sqlite3.IntegrityError:
                self.responder_json(409, {"erro": "Este colaborador já votou"})
                return

            self.responder_json(200, {"ok": True})
        finally:
            conexao.close()


            if __name__ == "__main__":
                print(f"Urna rodando em http://localhost:{PORTA}  (Ctrl + C para parar)")
                ThreadingHTTPServer(("localhost", PORTA), Urna).serve_forever()
