import http.server
import socketserver
import webbrowser
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('WebServer')

# Definir porta do servidor
PORT = 8000

# Mudar para o diretório cliente_web
os.chdir('cliente_web')

# Classe personalizada para lidar com requisições
class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(f"{self.client_address[0]} - {format%args}")
    
    def end_headers(self):
        # Adicionar cabeçalhos para evitar problemas de cache
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    # Redirecionar / para index.html
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Iniciar servidor
handler = CustomRequestHandler
httpd = socketserver.TCPServer(("", PORT), handler)

logger.info(f"Servidor rodando na porta {PORT}")
logger.info(f"Abra http://localhost:{PORT}/ no seu navegador")
logger.info(f"Diretório: {os.getcwd()}")

# Abrir navegador automaticamente
webbrowser.open(f'http://localhost:{PORT}/')

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    logger.info("Servidor encerrado.")
    httpd.server_close()
