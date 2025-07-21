import logging
from spyne import Application, rpc, ServiceBase, Unicode, Integer, Array, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import json
import os
import uuid

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

# Diretório de dados
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')

# Inicialização do arquivo de dados
if not os.path.exists(PLAYERS_FILE):
    with open(PLAYERS_FILE, 'w') as f:
        json.dump([], f)

# Classes de modelos
class PlayerStats(ComplexModel):
    __namespace__ = 'http://games.tictactoe.org/player'
    
    player_id = Unicode
    username = Unicode
    games_played = Integer
    games_won = Integer
    games_lost = Integer
    games_drawn = Integer

# Serviço de jogadores
class PlayerService(ServiceBase):
    __namespace__ = 'http://games.tictactoe.org/player'
    
    @rpc(Unicode, _returns=Unicode)
    def register_player(ctx, username):
        """
        Registra um novo jogador.
        
        @param username: Nome de usuário do jogador
        @return: ID do jogador
        """
        players = []
        try:
            with open(PLAYERS_FILE, 'r') as f:
                players = json.load(f)
        except:
            pass
        
        # Verificar se o nome de usuário já existe
        for player in players:
            if player.get('username') == username:
                return player.get('player_id')
        
        # Criar novo jogador
        player_id = str(uuid.uuid4())
        new_player = {
            'player_id': player_id,
            'username': username,
            'games_played': 0,
            'games_won': 0,
            'games_lost': 0,
            'games_drawn': 0
        }
        
        players.append(new_player)
        
        with open(PLAYERS_FILE, 'w') as f:
            json.dump(players, f, indent=2)
        
        return player_id
    
    @rpc(Unicode, _returns=PlayerStats)
    def get_player_stats(ctx, player_id):
        """
        Obtém estatísticas de um jogador pelo ID.
        
        @param player_id: ID do jogador
        @return: Estatísticas do jogador
        """
        try:
            with open(PLAYERS_FILE, 'r') as f:
                players = json.load(f)
            
            for player in players:
                if player.get('player_id') == player_id:
                    stats = PlayerStats(
                        player_id=player.get('player_id'),
                        username=player.get('username'),
                        games_played=player.get('games_played', 0),
                        games_won=player.get('games_won', 0),
                        games_lost=player.get('games_lost', 0),
                        games_drawn=player.get('games_drawn', 0)
                    )
                    return stats
        except Exception as e:
            logging.error(f"Erro ao obter estatísticas do jogador: {e}")
        
        return PlayerStats(
            player_id='',
            username='',
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0
        )
    
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def record_game_result(ctx, player_id, result, opponent_id=None):
        """
        Registra o resultado de um jogo para um jogador.
        
        @param player_id: ID do jogador
        @param result: Resultado ('W' para vitória, 'L' para derrota, 'D' para empate)
        @param opponent_id: ID do oponente (opcional)
        @return: Mensagem de confirmação
        """
        try:
            with open(PLAYERS_FILE, 'r') as f:
                players = json.load(f)
            
            player_found = False
            for player in players:
                if player.get('player_id') == player_id:
                    player_found = True
                    player['games_played'] = player.get('games_played', 0) + 1
                    
                    if result == 'W':
                        player['games_won'] = player.get('games_won', 0) + 1
                    elif result == 'L':
                        player['games_lost'] = player.get('games_lost', 0) + 1
                    elif result == 'D':
                        player['games_drawn'] = player.get('games_drawn', 0) + 1
            
            if not player_found:
                return "Jogador não encontrado"
            
            # Atualizar oponente se fornecido
            if opponent_id:
                for player in players:
                    if player.get('player_id') == opponent_id:
                        player['games_played'] = player.get('games_played', 0) + 1
                        
                        if result == 'W':
                            player['games_lost'] = player.get('games_lost', 0) + 1
                        elif result == 'L':
                            player['games_won'] = player.get('games_won', 0) + 1
                        elif result == 'D':
                            player['games_drawn'] = player.get('games_drawn', 0) + 1
            
            with open(PLAYERS_FILE, 'w') as f:
                json.dump(players, f, indent=2)
            
            return "Resultado do jogo registrado com sucesso"
        
        except Exception as e:
            logging.error(f"Erro ao registrar resultado do jogo: {e}")
            return f"Erro: {e}"
    
    @rpc(_returns=Array(PlayerStats))
    def list_all_players(ctx):
        """
        Lista todos os jogadores registrados.
        
        @return: Lista de estatísticas de jogadores
        """
        result = []
        try:
            with open(PLAYERS_FILE, 'r') as f:
                players = json.load(f)
            
            for player in players:
                stats = PlayerStats(
                    player_id=player.get('player_id'),
                    username=player.get('username'),
                    games_played=player.get('games_played', 0),
                    games_won=player.get('games_won', 0),
                    games_lost=player.get('games_lost', 0),
                    games_drawn=player.get('games_drawn', 0)
                )
                result.append(stats)
        except Exception as e:
            logging.error(f"Erro ao listar jogadores: {e}")
        
        return result

# Configuração da aplicação SOAP
application = Application([PlayerService], 
                          tns='http://games.tictactoe.org/player',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    # Iniciar servidor
    server = make_server('0.0.0.0', 8002, wsgi_application)
    print("Servidor SOAP iniciado em http://localhost:8002")
    print("WSDL disponível em http://localhost:8002/?wsdl")
    
    server.serve_forever()
