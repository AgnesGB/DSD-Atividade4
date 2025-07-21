import requests
import json

def test_soap_server():
    """
    Script para testar o servidor SOAP usando HTTP diretamente.
    Isso é útil para depuração rápida.
    """
    
    # URL do servidor SOAP
    url = "http://localhost:8002"
    
    # Headers para a solicitação SOAP
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://games.tictactoe.org/player#register_player"
    }
    
    # Corpo da solicitação SOAP para registrar um jogador
    soap_body = """<?xml version="1.0" encoding="UTF-8"?>
    <soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/" 
                       xmlns:tns="http://games.tictactoe.org/player">
        <soap11env:Body>
            <tns:register_player>
                <tns:username>TestPlayer</tns:username>
            </tns:register_player>
        </soap11env:Body>
    </soap11env:Envelope>"""
    
    try:
        response = requests.post(url, headers=headers, data=soap_body)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{response.text}")
        
        # Solicitar estatísticas do jogador
        headers["SOAPAction"] = "http://games.tictactoe.org/player#list_all_players"
        
        soap_body = """<?xml version="1.0" encoding="UTF-8"?>
        <soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/" 
                       xmlns:tns="http://games.tictactoe.org/player">
            <soap11env:Body>
                <tns:list_all_players>
                </tns:list_all_players>
            </soap11env:Body>
        </soap11env:Envelope>"""
        
        response = requests.post(url, headers=headers, data=soap_body)
        print(f"\nLista de Jogadores Status Code: {response.status_code}")
        print(f"Response:\n{response.text}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_soap_server()
