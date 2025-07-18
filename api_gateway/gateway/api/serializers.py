from rest_framework import serializers

class GameSerializer(serializers.Serializer):
    """Serializer para jogos"""
    id = serializers.UUIDField(read_only=True)
    board = serializers.CharField(read_only=True)
    player_x = serializers.CharField()
    player_o = serializers.CharField(required=False, allow_null=True)
    current_turn = serializers.CharField(read_only=True)
    winner = serializers.CharField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class GameListSerializer(serializers.Serializer):
    """Serializer para listar jogos"""
    id = serializers.UUIDField(read_only=True)
    player_x = serializers.CharField()
    player_o = serializers.CharField(required=False, allow_null=True)
    current_turn = serializers.CharField(read_only=True)
    winner = serializers.CharField(read_only=True, allow_null=True)

class PlayerSerializer(serializers.Serializer):
    """Serializer para jogadores"""
    player_id = serializers.CharField(read_only=True)
    username = serializers.CharField()
    games_played = serializers.IntegerField(read_only=True)
    games_won = serializers.IntegerField(read_only=True)
    games_lost = serializers.IntegerField(read_only=True)
    games_drawn = serializers.IntegerField(read_only=True)

class PlayerStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de jogadores"""
    player_id = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    games_played = serializers.IntegerField(read_only=True)
    games_won = serializers.IntegerField(read_only=True)
    games_lost = serializers.IntegerField(read_only=True)
    games_drawn = serializers.IntegerField(read_only=True)

class GameMoveSerializer(serializers.Serializer):
    """Serializer para movimentos em um jogo"""
    player_name = serializers.CharField()
    position = serializers.IntegerField(min_value=0, max_value=8)

class GameResultSerializer(serializers.Serializer):
    """Serializer para registrar resultados de jogos"""
    player_id = serializers.CharField()
    result = serializers.ChoiceField(choices=['W', 'L', 'D'])
    opponent_id = serializers.CharField(required=False, allow_null=True)
