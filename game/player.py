class PlayerInfo:
    def __init__(self, board, start, region):
        self.board = board
        self.start = start
        self.region = region

    @property
    def color(self):
        #boja regiona
        return self.board.colors[self.start]

    @property
    def size(self):
        return len(self.region)
