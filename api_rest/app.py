from flask import Flask, request, jsonify
from uuid import uuid4
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir CORS para requisições de diferentes origens
jogos = {}

def novo_tabuleiro():
    return ["" for _ in range(9)]

def verificar_vitoria(tabuleiro, simbolo):
    # Verificar linhas
    for i in range(0, 9, 3):
        if tabuleiro[i] == tabuleiro[i+1] == tabuleiro[i+2] == simbolo:
            return True
    
    # Verificar colunas
    for i in range(3):
        if tabuleiro[i] == tabuleiro[i+3] == tabuleiro[i+6] == simbolo:
            return True
    
    # Verificar diagonais
    if tabuleiro[0] == tabuleiro[4] == tabuleiro[8] == simbolo:
        return True
    if tabuleiro[2] == tabuleiro[4] == tabuleiro[6] == simbolo:
        return True
    
    return False

def verificar_empate(tabuleiro):
    return all(posicao != "" for posicao in tabuleiro)

@app.route("/games", methods=["POST"])
def criar_jogo():
    data = request.json or {}
    player_name = data.get("playerName", "Jogador X")
    
    game_id = str(uuid4())
    jogos[game_id] = {
        "tabuleiro": novo_tabuleiro(), 
        "turno": "X", 
        "status": "waiting_opponent",  # Aguardando segundo jogador
        "jogador_x": {"nome": player_name, "simbolo": "X"},
        "jogador_o": None,
        "vencedor": None
    }
    
    return jsonify({
        "gameId": game_id, 
        "jogador": "X",
        "playerName": player_name,
        "status": "waiting_opponent",
        "links": [
            {"rel": "self", "href": f"/games/{game_id}"},
            {"rel": "join", "href": f"/games/{game_id}/join"}
        ]
    }), 201

@app.route("/games/<game_id>/join", methods=["POST"])
def entrar_jogo(game_id):
    jogo = jogos.get(game_id)
    if not jogo:
        return jsonify({"erro": "Jogo não encontrado"}), 404
    
    if jogo["status"] != "waiting_opponent":
        return jsonify({"erro": "Jogo já possui dois jogadores"}), 400
    
    data = request.json or {}
    player_name = data.get("playerName", "Jogador O")
    
    jogo["jogador_o"] = {"nome": player_name, "simbolo": "O"}
    jogo["status"] = "in_progress"
    
    return jsonify({
        "gameId": game_id,
        "jogador": "O",
        "playerName": player_name,
        "status": "in_progress"
    })

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
    jogador = data.get("jogador")  # "X" ou "O"
    
    jogo = jogos.get(game_id)
    if not jogo:
        return jsonify({"erro": "Jogo não encontrado"}), 404
    
    if jogo["status"] != "in_progress":
        return jsonify({"erro": "Jogo não está em andamento"}), 400
    
    if jogador != jogo["turno"]:
        return jsonify({"erro": "Não é seu turno"}), 400
    
    if not (0 <= pos <= 8) or jogo["tabuleiro"][pos] != "":
        return jsonify({"erro": "Movimento inválido"}), 400
    
    # Realizar o movimento
    jogo["tabuleiro"][pos] = jogador
    
    # Verificar vitória
    if verificar_vitoria(jogo["tabuleiro"], jogador):
        jogo["status"] = "completed"
        jogo["vencedor"] = jogador
        vencedor_nome = jogo["jogador_x"]["nome"] if jogador == "X" else jogo["jogador_o"]["nome"]
        return jsonify({
            "tabuleiro": jogo["tabuleiro"],
            "status": "completed",
            "vencedor": jogador,
            "vencedor_nome": vencedor_nome
        })
    
    # Verificar empate
    if verificar_empate(jogo["tabuleiro"]):
        jogo["status"] = "completed"
        jogo["vencedor"] = "empate"
        return jsonify({
            "tabuleiro": jogo["tabuleiro"],
            "status": "completed",
            "vencedor": "empate"
        })
    
    # Trocar turno
    jogo["turno"] = "O" if jogador == "X" else "X"
    
    return jsonify({
        "tabuleiro": jogo["tabuleiro"],
        "status": jogo["status"],
        "turno": jogo["turno"]
    })

@app.route("/games/list", methods=["GET"])
def listar_jogos():
    jogos_disponiveis = []
    for game_id, jogo in jogos.items():
        if jogo["status"] == "waiting_opponent":
            jogos_disponiveis.append({
                "gameId": game_id,
                "criador": jogo["jogador_x"]["nome"],
                "status": jogo["status"]
            })
    return jsonify({"jogos": jogos_disponiveis})

if __name__ == "__main__":
    app.run(port=5001)