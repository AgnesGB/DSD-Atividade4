from http.server import HTTPServer, BaseHTTPRequestHandler
import xml.etree.ElementTree as ET
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ranking dos jogadores
rankings = {"Agnes": 10, "João": 8, "Maria": 15, "Carlos": 7}

# WSDL modelo
WSDL = '''<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions 
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tns="http://jogodavelha.soap"
    targetNamespace="http://jogodavelha.soap">
    
    <wsdl:types>
        <xs:schema targetNamespace="http://jogodavelha.soap">
            <xs:element name="getPlayerRankingRequest">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="name" type="xs:string"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="getPlayerRankingResponse">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="ranking" type="xs:int"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>
    </wsdl:types>
    
    <wsdl:message name="getPlayerRankingRequest">
        <wsdl:part name="parameters" element="tns:getPlayerRankingRequest"/>
    </wsdl:message>
    <wsdl:message name="getPlayerRankingResponse">
        <wsdl:part name="parameters" element="tns:getPlayerRankingResponse"/>
    </wsdl:message>
    
    <wsdl:portType name="GameService">
        <wsdl:operation name="getPlayerRanking">
            <wsdl:input message="tns:getPlayerRankingRequest"/>
            <wsdl:output message="tns:getPlayerRankingResponse"/>
        </wsdl:operation>
    </wsdl:portType>
    
    <wsdl:binding name="GameServiceSoap" type="tns:GameService">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="getPlayerRanking">
            <soap:operation soapAction="http://jogodavelha.soap/getPlayerRanking"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    
    <wsdl:service name="GameService">
        <wsdl:port name="GameServiceSoap" binding="tns:GameServiceSoap">
            <soap:address location="http://localhost:5002"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>
'''

class SOAPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/?wsdl' or self.path == '/wsdl':
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(WSDL.encode())
            logger.info("WSDL enviado ao cliente")
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Servidor SOAP em execucao. Acesse /?wsdl para o arquivo WSDL")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        logger.info(f"Requisição SOAP recebida: {post_data[:200]}...")
        
        try:
            # Procurar o nome do jogador na requisição SOAP
            name_match = re.search(r'<.*:name>(.*)</.*:name>', post_data)
            if not name_match:
                name_match = re.search(r'<name>(.*)</name>', post_data)
                
            if name_match:
                player_name = name_match.group(1)
                logger.info(f"Nome do jogador encontrado: {player_name}")
                
                # Obter o ranking do jogador
                player_ranking = rankings.get(player_name, 0)
                logger.info(f"Ranking do jogador {player_name}: {player_ranking}")
                
                # Construir resposta SOAP
                soap_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getPlayerRankingResponse xmlns="http://jogodavelha.soap">
      <ranking>{player_ranking}</ranking>
    </getPlayerRankingResponse>
  </soap:Body>
</soap:Envelope>'''
                
                self.send_response(200)
                self.send_header('Content-type', 'text/xml')
                self.end_headers()
                self.wfile.write(soap_response.encode())
            else:
                logger.error("Nome do jogador não encontrado na requisição")
                self.send_response(400)
                self.send_header('Content-type', 'text/xml')
                self.end_headers()
                self.wfile.write(b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><soap:Fault><faultcode>soap:Client</faultcode><faultstring>Nome do jogador nao encontrado na requisicao</faultstring></soap:Fault></soap:Body></soap:Envelope>')
        except Exception as e:
            logger.error(f"Erro ao processar requisição SOAP: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(f'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><soap:Fault><faultcode>soap:Server</faultcode><faultstring>{str(e)}</faultstring></soap:Fault></soap:Body></soap:Envelope>'.encode())

if __name__ == "__main__":
    try:
        server_address = ('', 5002)
        httpd = HTTPServer(server_address, SOAPHandler)
        print("Iniciando servidor SOAP na porta 5002...")
        print("WSDL disponível em http://localhost:5002/?wsdl")
        httpd.serve_forever()
    except Exception as e:
        print(f"Erro ao iniciar o servidor SOAP: {e}")