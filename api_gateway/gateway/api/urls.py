from django.urls import path
from .views import (
    GamesView, GameDetailView, GameJoinView, GameMoveView,
    PlayersView, PlayerDetailView
)

urlpatterns = [
    # Rotas para jogos
    path('games/', GamesView.as_view(), name='games-list'),
    path('games/<uuid:game_id>/', GameDetailView.as_view(), name='game-detail'),
    path('games/<uuid:game_id>/join/', GameJoinView.as_view(), name='game-join'),
    path('games/<uuid:game_id>/move/', GameMoveView.as_view(), name='game-move'),
    
    # Rotas para jogadores
    path('players/', PlayersView.as_view(), name='players-list'),
    path('players/<str:player_id>/', PlayerDetailView.as_view(), name='player-detail'),
]
