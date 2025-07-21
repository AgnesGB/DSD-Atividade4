from django.db import models
import uuid

class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.CharField(max_length=9, default='---------')  # Tabuleiro 3x3 representado como string
    player_x = models.CharField(max_length=100)
    player_o = models.CharField(max_length=100, blank=True, null=True)
    current_turn = models.CharField(max_length=1, default='X')  # X ou O
    winner = models.CharField(max_length=1, blank=True, null=True)  # X, O ou empate (D)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Game {self.id} - {self.player_x} vs {self.player_o}"
    
    def is_valid_move(self, position):
        if position < 0 or position > 8:
            return False
        if self.board[position] != '-':
            return False
        if self.winner:
            return False
        return True
    
    def make_move(self, position):
        if not self.is_valid_move(position):
            return False
        
        board_list = list(self.board)
        board_list[position] = self.current_turn
        self.board = ''.join(board_list)
        
        # Verificar se há um vencedor
        if self.check_winner():
            self.winner = self.current_turn
        # Verificar se é empate
        elif '-' not in self.board:
            self.winner = 'D'
        else:
            # Alternar jogador
            self.current_turn = 'O' if self.current_turn == 'X' else 'X'
        
        self.save()
        return True
    
    def check_winner(self):
        # Linhas
        for i in range(0, 9, 3):
            if self.board[i] != '-' and self.board[i] == self.board[i+1] == self.board[i+2]:
                return True
        
        # Colunas
        for i in range(3):
            if self.board[i] != '-' and self.board[i] == self.board[i+3] == self.board[i+6]:
                return True
        
        # Diagonais
        if self.board[0] != '-' and self.board[0] == self.board[4] == self.board[8]:
            return True
        if self.board[2] != '-' and self.board[2] == self.board[4] == self.board[6]:
            return True
        
        return False
