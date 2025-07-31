from flask import Flask, request, jsonify
from uuid import uuid4

app = Flask(__name__)
jogos = {}

def novo_tabuleiro():
    return ["" for _ in range(9)]

@app.route("/games", methods=["POST"])
def criar_jogo():
    game_id = str(uuid4())
    jogos[game_id] = {"tabuleiro": novo_tabuleiro(), "turno": "X", "status": "in_progress"}
    return jsonify({"gameId": game_id, "links": [
        {"rel": "self", "href": f"/games/{game_id}"},
        {"rel": "move", "href": f"/games/{game_id}/move"}
    ]}), 201

@app.route("/games/<game_id>", methods=["GET"])
def obter_jogo(game_id):
    jogo = jogos.get(game_id)
    if not jogo:
        return jsonify({"erro": "Jogo não encontrado"}), 404
    return jsonify(jogo)

@app.route("/games/<game_id>/move", methods=["POST"])
def fazer_movimento(game_id):
    data = request.json
    pos = data.get("pos")
    jogo = jogos.get(game_id)
    if not jogo or not (0 <= pos <= 8):
        return jsonify({"erro": "Movimento inválido"}), 400
    if jogo["tabuleiro"][pos] != "":
        return jsonify({"erro": "Posição ocupada"}), 400

    jogo["tabuleiro"][pos] = jogo["turno"]
    jogo["turno"] = "O" if jogo["turno"] == "X" else "X"
    return jsonify(jogo)

if __name__ == "__main__":
    app.run(port=5001)