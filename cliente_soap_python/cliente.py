import requests
import logging
import xml.etree.ElementTree as ET
import re

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def consultar_ranking(nome):
    try:
        # URL do servidor SOAP
        url = 'http://localhost:5002'
        
        # Criando requisição SOAP
        soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://jogodavelha.soap">
  <soap:Body>
    <tns:getPlayerRankingRequest>
      <tns:name>{nome}</tns:name>
    </tns:getPlayerRankingRequest>
  </soap:Body>
</soap:Envelope>'''
        
        # Enviando requisição SOAP
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://jogodavelha.soap/getPlayerRanking'
        }
        
        print(f"Enviando requisição SOAP para obter ranking de {nome}...")
        response = requests.post(url, data=soap_request.encode('utf-8'), headers=headers)
        
        # Verificando resposta
        if response.status_code == 200:
            # Extrair o ranking da resposta
            ranking_match = re.search(r'<.*:ranking>(\d+)</.*:ranking>', response.text)
            if not ranking_match:
                ranking_match = re.search(r'<ranking>(\d+)</ranking>', response.text)
                
            if ranking_match:
                ranking = int(ranking_match.group(1))
                return ranking
            else:
                print("Erro: Não foi possível extrair o ranking da resposta SOAP.")
                print(f"Resposta: {response.text}")
                return 0
        else:
            print(f"Erro na requisição SOAP: {response.status_code}")
            print(response.text)
            return 0
    except Exception as e:
        print(f"Erro ao consultar o ranking: {e}")
        return 0

if __name__ == "__main__":
    try:
        # Obtendo o nome do jogador
        nome = input("Digite seu nome: ")
        
        # Consultando o ranking
        ranking = consultar_ranking(nome)
        
        # Exibindo resultado
        print(f"Ranking de {nome}: {ranking}")
    except Exception as e:
        print(f"Erro: {e}")
        print("Verifique se o servidor SOAP está em execução na porta 5002.")