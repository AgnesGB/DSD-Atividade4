from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Game
from .serializers import GameSerializer, MoveSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        game = self.get_object()
        
        if game.player_o:
            return Response({"detail": "Game is already full"}, status=status.HTTP_400_BAD_REQUEST)
        
        player_o = request.data.get('player_o')
        if not player_o:
            return Response({"detail": "Player O name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        game.player_o = player_o
        game.save()
        
        serializer = self.get_serializer(game)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        game = self.get_object()
        
        serializer = MoveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se é o jogador correto
        player = serializer.validated_data['player']
        if (game.current_turn == 'X' and player != game.player_x) or \
           (game.current_turn == 'O' and player != game.player_o):
            return Response({"detail": "Not your turn"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se o jogo já terminou
        if game.winner:
            return Response({"detail": "Game is already over"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fazer o movimento
        position = serializer.validated_data['position']
        if not game.make_move(position):
            return Response({"detail": "Invalid move"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(GameSerializer(game).data)
