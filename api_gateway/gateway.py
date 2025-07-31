from flask import Flask, jsonify, request, Response, send_from_directory
import requests
from zeep import Client
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir chamadas do cliente web
SOAP_URL = 'http://localhost:5002/?wsdl'
REST_URL = 'http://localhost:5001'

# Funções auxiliares para HATEOAS
def add_links(resource, game_id=None):
    links = [{"rel": "games", "href": "/api/games", "method": "POST", "description": "Criar novo jogo"}]
    
    if game_id:
        links.extend([
            {"rel": "self", "href": f"/api/games/{game_id}", "method": "GET", "description": "Obter estado do jogo"},
            {"rel": "move", "href": f"/api/games/{game_id}/move", "method": "POST", "description": "Fazer uma jogada"}
        ])
    
    links.append({"rel": "ranking", "href": "/api/ranking/{nome}", "method": "GET", "description": "Consultar ranking de um jogador"})
    
    if isinstance(resource, dict):
        resource["_links"] = links
    return resource

@app.route("/api", methods=["GET"])
def api_root():
    """Endpoint raiz que fornece documentação da API"""
    return jsonify(add_links({
        "name": "Jogo da Velha API Gateway",
        "description": "Gateway que integra serviços REST e SOAP para o jogo da velha",
        "version": "1.0"
    }))

@app.route("/api/games", methods=["POST"])
def criar_jogo():
    resp = requests.post(f"{REST_URL}/games")
    data = resp.json()
    game_id = data.get("gameId")
    return jsonify(add_links(data, game_id))

@app.route("/api/games/<gid>", methods=["GET"])
def jogo(gid):
    resp = requests.get(f"{REST_URL}/games/{gid}")
    data = resp.json()
    return jsonify(add_links(data, gid))

@app.route("/api/games/<gid>/move", methods=["POST"])
def mover(gid):
    resp = requests.post(f"{REST_URL}/games/{gid}/move", json=request.json)
    data = resp.json()
    return jsonify(add_links(data, gid))

@app.route("/api/ranking/<nome>", methods=["GET"])
def ranking(nome):
    # Usando requests para chamar o serviço SOAP diretamente
    soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://jogodavelha.soap">
  <soap:Body>
    <tns:getPlayerRankingRequest>
      <tns:name>{nome}</tns:name>
    </tns:getPlayerRankingRequest>
  </soap:Body>
</soap:Envelope>'''
    
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://jogodavelha.soap/getPlayerRanking'
    }
    
    try:
        response = requests.post('http://localhost:5002', data=soap_request.encode('utf-8'), headers=headers)
        
        if response.status_code == 200:
            # Extrair o ranking da resposta usando regex
            import re
            ranking_match = re.search(r'<.*:ranking>(\d+)</.*:ranking>', response.text)
            if not ranking_match:
                ranking_match = re.search(r'<ranking>(\d+)</ranking>', response.text)
                
            if ranking_match:
                resultado = int(ranking_match.group(1))
            else:
                resultado = 0
        else:
            resultado = 0
    except Exception:
        resultado = 0
    
    return jsonify(add_links({
        "nome": nome,
        "ranking": resultado,
        "tipo": "SOAP"
    }))

@app.route("/api/wsdl", methods=["GET"])
def get_wsdl():
    """Endpoint para obter o WSDL do serviço SOAP"""
    resp = requests.get(SOAP_URL)
    return Response(resp.content, mimetype='text/xml')

@app.route("/api/docs", methods=["GET"])
def get_docs():
    """Endpoint para servir a documentação Swagger"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(current_dir, "swagger.json")

@app.route("/swagger-ui", methods=["GET"])
def swagger_ui():
    """Redireciona para o Swagger UI usando o arquivo swagger.json"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin: 0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: "/api/docs",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    validatorUrl: null
                });
                window.ui = ui;
            };
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")