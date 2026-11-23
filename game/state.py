import random

from game.board import Board
from game.constants import MAX_K, MAX_N, MIN_K, MIN_N, NEUTRAL, P1, P2
from game.player import PlayerInfo


def _flood_fill(board, start):
    color = board.colors[start]
    region = {start}
    stack = [start]
    while stack:
        i = stack.pop()
        for j in board.neighbors[i]:
            if j not in region and board.colors[j] == color:
                region.add(j)
                stack.append(j)
    return region


class GameState:
    def __init__(self, board, players, current_player):
        self.board = board
        self.players = players
        self.current_player = current_player

    @classmethod
    def new(cls, n, k, first_player=P1):
        if not MIN_N <= n <= MAX_N:
            raise ValueError(f"N mora biti od {MIN_N} do {MAX_N}")
        if not MIN_K <= k <= MAX_K:
            raise ValueError(f"K mora biti od {MIN_K} do {MAX_K}")

        board = Board.random(n, k)
        starts = {P1: board.index(0, 0), P2: board.index(n - 1, n - 1)}

        # da pocetna polja imaju razlicite boje / mozda i ne mora?
        if board.colors[starts[P1]] == board.colors[starts[P2]]:
            other_colors = [c for c in range(k) if c != board.colors[starts[P1]]]
            board.colors[starts[P2]] = random.choice(other_colors)

        players = {}
        for player, start in starts.items():
            region = _flood_fill(board, start)
            for i in region:
                board.owners[i] = player
            players[player] = PlayerInfo(board, start, region)

        return cls(board, players, first_player)

    def opponent(self, player):
        return P2 if player == P1 else P1

    def legal_moves(self, player=None):
        if player is None:
            player = self.current_player
        me = self.players[player]
        enemy = self.players[self.opponent(player)]

        moves = set()
        for i in me.region:
            for j in self.board.neighbors[i]:
                owner = self.board.owners[j]
                if owner == NEUTRAL:
                    moves.add(self.board.colors[j])
                elif owner != player:
                    moves.add(enemy.color)
        moves.discard(me.color)
        return sorted(moves)

    def is_valid_move(self, color):
        if not isinstance(color, int) or isinstance(color, bool):
            return False
        return 0 <= color < self.board.k and color in self.legal_moves()

    def is_game_over(self):
        if any(info.size == 0 for info in self.players.values()):
            return True
        return not self.legal_moves()

    def winner(self):
        if not self.is_game_over():
            return None
        size1 = self.players[P1].size
        size2 = self.players[P2].size
        if size1 > size2:
            return P1
        if size2 > size1:
            return P2
        return NEUTRAL

    def __str__(self):
        lines = [str(self.board), f"Na potezu: P{self.current_player}"]
        for player, info in self.players.items():
            lines.append(f"P{player}: region {info.size} polja, boja {info.color}")
        return "\n".join(lines)
