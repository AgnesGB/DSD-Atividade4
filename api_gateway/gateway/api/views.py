from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .clients import RestServiceClient, SoapServiceClient
import logging

logger = logging.getLogger(__name__)

class GamesView(APIView):
    """
    Endpoint para gerenciar jogos.
    """
    
    def get(self, request):
        """Listar todos os jogos disponíveis"""
        try:
            rest_client = RestServiceClient()
            games = rest_client.list_games()
            
            # Adicionar links HATEOAS
            for game in games:
                game['_links'] = {
                    'self': {'href': f'/api/games/{game["id"]}'},
                    'join': {'href': f'/api/games/{game["id"]}/join'},
                    'move': {'href': f'/api/games/{game["id"]}/move'}
                }
            
            return Response(games)
        except Exception as e:
            logger.error(f"Error listing games: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Criar um novo jogo"""
        player_name = request.data.get('player_name')
        if not player_name:
            return Response({"error": "player_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Primeiro registrar o jogador no serviço SOAP
            soap_client = SoapServiceClient()
            player_id = soap_client.register_player(player_name)
            
            # Criar o jogo no serviço REST
            rest_client = RestServiceClient()
            game = rest_client.create_game(player_name)
            
            # Adicionar links HATEOAS
            game['_links'] = {
                'self': {'href': f'/api/games/{game["id"]}'},
                'join': {'href': f'/api/games/{game["id"]}/join'},
                'move': {'href': f'/api/games/{game["id"]}/move'},
                'player': {'href': f'/api/players/{player_id}'}
            }
            
            return Response(game, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating game: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GameDetailView(APIView):
    """
    Endpoint para gerenciar um jogo específico.
    """
    
    def get(self, request, game_id):
        """Obter detalhes de um jogo específico"""
        try:
            rest_client = RestServiceClient()
            game = rest_client.get_game(game_id)
            
            # Adicionar links HATEOAS
            game['_links'] = {
                'self': {'href': f'/api/games/{game_id}'},
                'collection': {'href': '/api/games'},
                'join': {'href': f'/api/games/{game_id}/join'},
                'move': {'href': f'/api/games/{game_id}/move'}
            }
            
            return Response(game)
        except Exception as e:
            logger.error(f"Error getting game {game_id}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GameJoinView(APIView):
    """
    Endpoint para entrar em um jogo.
    """
    
    def post(self, request, game_id):
        """Entrar em um jogo existente"""
        player_name = request.data.get('player_name')
        if not player_name:
            return Response({"error": "player_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Primeiro registrar o jogador no serviço SOAP
            soap_client = SoapServiceClient()
            player_id = soap_client.register_player(player_name)
            
            # Entrar no jogo no serviço REST
            rest_client = RestServiceClient()
            game = rest_client.join_game(game_id, player_name)
            
            # Adicionar links HATEOAS
            game['_links'] = {
                'self': {'href': f'/api/games/{game_id}'},
                'collection': {'href': '/api/games'},
                'move': {'href': f'/api/games/{game_id}/move'},
                'player': {'href': f'/api/players/{player_id}'}
            }
            
            return Response(game)
        except Exception as e:
            logger.error(f"Error joining game {game_id}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GameMoveView(APIView):
    """
    Endpoint para fazer movimentos em um jogo.
    """
    
    def post(self, request, game_id):
        """Fazer um movimento em um jogo"""
        player_name = request.data.get('player_name')
        position = request.data.get('position')
        
        if not player_name:
            return Response({"error": "player_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        if position is None:
            return Response({"error": "position is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            rest_client = RestServiceClient()
            game = rest_client.make_move(game_id, player_name, position)
            
            # Adicionar links HATEOAS
            game['_links'] = {
                'self': {'href': f'/api/games/{game_id}'},
                'collection': {'href': '/api/games'},
            }
            
            # Verificar se o jogo terminou
            if game.get('winner'):
                # Registrar resultado no serviço SOAP
                try:
                    soap_client = SoapServiceClient()
                    
                    # Obter IDs dos jogadores
                    # Na prática, seria necessário ter um mapeamento entre nomes e IDs
                    # Aqui estamos simplificando, poderíamos armazenar isso em um banco de dados
                    
                    if game['winner'] == 'X':
                        winner_name = game['player_x']
                        loser_name = game['player_o']
                        winner_result = 'W'
                        loser_result = 'L'
                    elif game['winner'] == 'O':
                        winner_name = game['player_o']
                        loser_name = game['player_x']
                        winner_result = 'W'
                        loser_result = 'L'
                    else:  # Empate
                        winner_name = game['player_x']
                        loser_name = game['player_o']
                        winner_result = 'D'
                        loser_result = 'D'
                    
                    # Registrar resultados
                    winner_id = soap_client.register_player(winner_name)
                    loser_id = soap_client.register_player(loser_name)
                    
                    soap_client.record_game_result(winner_id, winner_result, loser_id)
                    soap_client.record_game_result(loser_id, loser_result, winner_id)
                    
                    # Adicionar link para estatísticas
                    game['_links']['player_x_stats'] = {'href': f'/api/players/{winner_id}'}
                    game['_links']['player_o_stats'] = {'href': f'/api/players/{loser_id}'}
                    
                except Exception as e:
                    logger.error(f"Error recording game result: {e}")
            
            return Response(game)
        except Exception as e:
            logger.error(f"Error making move in game {game_id}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlayersView(APIView):
    """
    Endpoint para gerenciar jogadores.
    """
    
    def get(self, request):
        """Listar todos os jogadores"""
        try:
            soap_client = SoapServiceClient()
            players = soap_client.list_all_players()
            
            # Adicionar links HATEOAS
            for player in players:
                player['_links'] = {
                    'self': {'href': f'/api/players/{player["player_id"]}'},
                }
            
            return Response(players)
        except Exception as e:
            logger.error(f"Error listing players: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Registrar um novo jogador"""
        username = request.data.get('username')
        if not username:
            return Response({"error": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            soap_client = SoapServiceClient()
            player_id = soap_client.register_player(username)
            
            response_data = {
                'player_id': player_id,
                '_links': {
                    'self': {'href': f'/api/players/{player_id}'},
                    'collection': {'href': '/api/players'},
                    'games': {'href': '/api/games'}
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error registering player: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlayerDetailView(APIView):
    """
    Endpoint para gerenciar um jogador específico.
    """
    
    def get(self, request, player_id):
        """Obter estatísticas de um jogador específico"""
        try:
            soap_client = SoapServiceClient()
            player = soap_client.get_player_stats(player_id)
            
            # Adicionar links HATEOAS
            player['_links'] = {
                'self': {'href': f'/api/players/{player_id}'},
                'collection': {'href': '/api/players'},
                'games': {'href': '/api/games'}
            }
            
            return Response(player)
        except Exception as e:
            logger.error(f"Error getting player {player_id}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
