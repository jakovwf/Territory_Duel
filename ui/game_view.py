import tkinter as tk
from typing import Callable, List

from game.constants import NEUTRAL, P1, P2
from game.state import GameState
from ui.config import GameConfig

DOT_COLORS = {P1: "black", P2: "white"}


class GameView(tk.Frame):
    """Prikaz igre: tabla, paleta, status i dugmad."""

    def __init__(self, master: tk.Misc, state: GameState, config: GameConfig,
                 on_back: Callable[[], None], from_file: bool = False) -> None:
        super().__init__(master, padx=10, pady=10)
        self.state = state
        self.config = config
        self.on_back = on_back
        self.from_file = from_file
        self.color_buttons: List[tk.Button] = []

        self._build()
        self._build_palette()
        self.after_move()

    # ---------- izgled ----------

    def _build(self) -> None:
        # tabla
        self.canvas = tk.Canvas(self, width=450, height=450, bg="white", highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        # paleta
        self.palette_frame = tk.Frame(self)
        self.palette_frame.pack(side="top", pady=5)

        # status
        self.turn_label = tk.Label(self, text="", font=("Arial", 11, "bold"))
        self.turn_label.pack(side="top")
        self.size_label = tk.Label(self, text="")
        self.size_label.pack(side="top")
        self.message_label = tk.Label(self, text="", fg="blue")
        self.message_label.pack(side="top")

        # dugmad
        buttons = tk.Frame(self)
        buttons.pack(side="top", pady=5)
        tk.Button(buttons, text="Nazad u meni", command=self.on_back).pack(side="left", padx=5)
        self.new_game_button = tk.Button(buttons, text="Nova igra", command=self.new_game)
        self.new_game_button.pack(side="left", padx=5)
        if self.from_file:
            self.new_game_button.config(state="disabled")

    def _build_palette(self) -> None:
        # po jedno dugme za svaku od K boja
        for b in self.color_buttons:
            b.destroy()
        self.color_buttons = []
        for color in range(self.state.board.k):
            b = tk.Button(self.palette_frame, width=3, bg=self.state.board.palette[color],
                          activebackground=self.state.board.palette[color],
                          disabledforeground="black",
                          command=lambda c=color: self.on_color_chosen(c))
            b.pack(side="left", padx=2)
            self.color_buttons.append(b)

    # ---------- crtanje ----------

    def redraw(self) -> None:
        # iscrtava celu tablu iz stanja
        board = self.state.board
        n = board.n
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cell = max(1, min(width, height) // n)
        x0 = (width - cell * n) // 2
        y0 = (height - cell * n) // 2

        starts = {info.start: player for player, info in self.state.players.items()}

        for i in range(n * n):
            r, c = board.position(i)
            x = x0 + c * cell
            y = y0 + r * cell
            self.canvas.create_rectangle(x, y, x + cell, y + cell,
                                         fill=board.palette[board.colors[i]], outline="gray30")
            owner = board.owners[i]
            cx, cy = x + cell / 2, y + cell / 2
            if i in starts:
                # oznaka pocetnog polja
                player = starts[i]
                size = max(6, cell // 3)
                self.canvas.create_text(cx, cy, text=f"P{player}",
                                        fill=DOT_COLORS[player], font=("Arial", size, "bold"))
            elif owner != NEUTRAL:
                # tackica za polje u regionu igraca
                d = max(2, cell // 6)
                self.canvas.create_oval(cx - d, cy - d, cx + d, cy + d,
                                        fill=DOT_COLORS[owner], outline=DOT_COLORS[owner])

    def update_palette(self) -> None:
        # dozvoljene boje su samo one iz legal_moves(); ostale su onemogucene i oznacene sa X
        human_turn = not self.config.is_computer(self.state.current_player)
        active = human_turn and not self.state.is_game_over()
        legal = set(self.state.legal_moves()) if active else set()
        for color, b in enumerate(self.color_buttons):
            if color in legal:
                b.config(state="normal", text="")
            else:
                b.config(state="disabled", text="X")

    def update_status(self) -> None:
        player = self.state.current_player
        who = "računar" if self.config.is_computer(player) else "čovek"
        self.turn_label.config(text=f"Na potezu: P{player} ({who})")
        p1 = self.state.players[P1].size
        p2 = self.state.players[P2].size
        self.size_label.config(text=f"Region P1: {p1}   Region P2: {p2}")

    def set_message(self, text: str) -> None:
        self.message_label.config(text=text)

    # ---------- tok igre ----------

    def on_color_chosen(self, color: int) -> None:
        # jedino mesto za izbor poteza coveka
        if self.state.is_game_over():
            return
        if self.config.is_computer(self.state.current_player):
            return
        if self.state.is_valid_move(color):
            self.set_message(f"Potez je ispravan (boja {color})")
            # TODO faza II: primeniti potez, promeniti current_player, redraw()
            # posle toga pozvati self.after_move()
        else:
            self.set_message(f"Potez nije ispravan (boja {color})")

    def after_move(self) -> None:
        # poziva se posle svakog poteza (i na pocetku partije)
        self.update_status()
        self.update_palette()
        self.redraw()
        if self.state.is_game_over():
            winner = self.state.winner()
            if winner == NEUTRAL:
                self.set_message("Kraj igre: nerešeno")
            else:
                self.set_message(f"Kraj igre: pobednik je P{winner}")
            for b in self.color_buttons:
                b.config(state="disabled")
            return
        if self.config.is_computer(self.state.current_player):
            self.request_computer_move()

    def request_computer_move(self) -> None:
        # TODO faza III: pozvati Min-Max (preko root.after, da se prozor ne blokira)
        self.set_message("Računar je na potezu (još nije implementirano)")

    def new_game(self) -> None:
        # ista konfiguracija, novo nasumicno stanje
        if self.from_file:
            return
        self.state = GameState.new(self.config.n, self.config.k,
                                   first_player=self.config.first_player)
        self.set_message("")
        self._build_palette()
        self.after_move()
