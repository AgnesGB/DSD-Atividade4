from rest_framework import serializers
from .models import Game

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'board', 'player_x', 'player_o', 'current_turn', 'winner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'board', 'current_turn', 'winner', 'created_at', 'updated_at']

class MoveSerializer(serializers.Serializer):
    position = serializers.IntegerField(min_value=0, max_value=8)
    player = serializers.CharField(max_length=100)
