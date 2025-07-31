import http.server
import socketserver
import webbrowser
import os

# Definir porta do servidor
PORT = 8000

# Verificar se o diretório cliente_web existe
if os.path.exists('cliente_web'):
    print(f"Diretório cliente_web encontrado: {os.path.abspath('cliente_web')}")
    os.chdir('cliente_web')
else:
    print(f"Diretório cliente_web NÃO encontrado. Diretório atual: {os.getcwd()}")
    print("Listando diretórios:")
    for item in os.listdir():
        if os.path.isdir(item):
            print(f" - {item}/")

# Usar o handler padrão
handler = http.server.SimpleHTTPRequestHandler

# Configurar servidor
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Servidor iniciado na porta {PORT}")
    print(f"Diretório sendo servido: {os.getcwd()}")
    print(f"Abra http://localhost:{PORT}/ no seu navegador")
    
    # Abrir navegador
    webbrowser.open(f'http://localhost:{PORT}/')
    
    # Iniciar o servidor
    httpd.serve_forever()
