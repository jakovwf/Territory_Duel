import random

from game.constants import NEUTRAL, P1, P2, PALETTE


class Board:
    """podaci o tabli, tabla je niz, polje(r, c) ima indeks r * n + c."""

    def __init__(self, n, k, palette, colors, owners):
        self.n = n
        self.k = k
        self.palette = palette
        self.colors = colors
        self.owners = owners
        self.neighbors = self._build_neighbors()

    @classmethod
    def random(cls, n, k):
        colors = [random.randrange(k) for _ in range(n * n)]
        owners = [NEUTRAL] * (n * n)
        return cls(n, k, PALETTE[:k], colors, owners)

    def index(self, r, c):
        return r * self.n + c

    def position(self, i):
        return divmod(i, self.n)

    def _build_neighbors(self):
        neighbors = []
        for i in range(self.n * self.n):
            r, c = self.position(i)
            near = []
            if r > 0:
                near.append(self.index(r - 1, c))
            if r < self.n - 1:
                near.append(self.index(r + 1, c))
            if c > 0:
                near.append(self.index(r, c - 1))
            if c < self.n - 1:
                near.append(self.index(r, c + 1))
            neighbors.append(near)
        return neighbors

    def __str__(self):
        # A je P1, B je P2, . je neutralno
        marks = {NEUTRAL: ".", P1: "A", P2: "B"}
        rows = []
        for r in range(self.n):
            cells = []
            for c in range(self.n):
                i = self.index(r, c)
                cells.append(f"{self.colors[i]:>2}{marks[self.owners[i]]}")
            rows.append(" ".join(cells))
        return "\n".join(rows)
