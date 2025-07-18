import requests
from zeep import Client
from zeep.transports import Transport
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RestServiceClient:
    """Cliente para o serviço REST de jogos"""
    
    def __init__(self):
        self.base_url = settings.REST_SERVICE_URL
    
    def create_game(self, player_name):
        """Criar novo jogo"""
        url = f"{self.base_url}/api/games/"
        data = {"player_x": player_name}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error creating game: {e}")
            raise
    
    def get_game(self, game_id):
        """Obter informações do jogo"""
        url = f"{self.base_url}/api/games/{game_id}/"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error getting game {game_id}: {e}")
            raise
    
    def list_games(self):
        """Listar todos os jogos"""
        url = f"{self.base_url}/api/games/"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error listing games: {e}")
            raise
    
    def join_game(self, game_id, player_name):
        """Entrar em um jogo existente"""
        url = f"{self.base_url}/api/games/{game_id}/join/"
        data = {"player_o": player_name}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error joining game {game_id}: {e}")
            raise
    
    def make_move(self, game_id, player_name, position):
        """Fazer um movimento no jogo"""
        url = f"{self.base_url}/api/games/{game_id}/move/"
        data = {"player": player_name, "position": position}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error making move in game {game_id}: {e}")
            raise

class SoapServiceClient:
    """Cliente para o serviço SOAP de jogadores"""
    
    def __init__(self):
        self.wsdl_url = settings.SOAP_SERVICE_WSDL
        self.client = Client(self.wsdl_url)
    
    def register_player(self, username):
        """Registrar novo jogador"""
        try:
            result = self.client.service.register_player(username)
            return result
        except Exception as e:
            logger.error(f"Error registering player: {e}")
            raise
    
    def get_player_stats(self, player_id):
        """Obter estatísticas do jogador"""
        try:
            result = self.client.service.get_player_stats(player_id)
            # Converter para dicionário para facilitar a serialização JSON
            return {
                'player_id': result.player_id,
                'username': result.username,
                'games_played': result.games_played,
                'games_won': result.games_won,
                'games_lost': result.games_lost,
                'games_drawn': result.games_drawn
            }
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            raise
    
    def record_game_result(self, player_id, result, opponent_id=None):
        """Registrar resultado de jogo"""
        try:
            result = self.client.service.record_game_result(player_id, result, opponent_id)
            return result
        except Exception as e:
            logger.error(f"Error recording game result: {e}")
            raise
    
    def list_all_players(self):
        """Listar todos os jogadores"""
        try:
            result = self.client.service.list_all_players()
            # Converter para lista de dicionários
            players = []
            for player in result:
                players.append({
                    'player_id': player.player_id,
                    'username': player.username,
                    'games_played': player.games_played,
                    'games_won': player.games_won,
                    'games_lost': player.games_lost,
                    'games_drawn': player.games_drawn
                })
            return players
        except Exception as e:
            logger.error(f"Error listing players: {e}")
            raise
