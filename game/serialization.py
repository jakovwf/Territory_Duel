import json

from game.board import Board
from game.constants import P1, P2
from game.player import PlayerInfo
from game.state import GameState

# f-ja za ucitavanje test statova, za testiranje dok faza 2 nije gotova
def load_state(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    palette_dict = data["palette"]
    palette = [palette_dict[key] for key in sorted(palette_dict, key=int)]

    rows = data["board"]
    n = len(rows)
    k = len(palette)

    colors = []
    owners = []
    for row in rows:
        for color, owner in row:
            colors.append(color)
            owners.append(owner)

    board = Board(n, k, palette, colors, owners)

    starts = {P1: board.index(0, 0), P2: board.index(n - 1, n - 1)}
    players = {}
    for player, start in starts.items():
        region = {i for i in range(n * n) if owners[i] == player}
        players[player] = PlayerInfo(board, start, region)

    return GameState(board, players, data["current_player"])
