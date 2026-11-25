import tkinter as tk
from typing import Optional

from game.state import GameState
from ui.config import GameConfig
from ui.game_view import GameView
from ui.menu import MenuFrame


class App:
    """Glavni prozor; menja meni i prikaz igre u istom prozoru."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Borba za teritoriju")
        self.root.minsize(400, 450)
        self.current: Optional[tk.Frame] = None
        self.show_menu()

    def _set_frame(self, frame: tk.Frame) -> None:
        # uklanja stari frame i prikazuje novi
        if self.current is not None:
            self.current.destroy()
        self.current = frame
        frame.pack(fill="both", expand=True)

    def show_menu(self) -> None:
        self._set_frame(MenuFrame(self.root, on_start=self.show_game))

    def show_game(self, state: GameState, config: GameConfig, from_file: bool) -> None:
        self._set_frame(GameView(self.root, state, config, on_back=self.show_menu,
                                 from_file=from_file))

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
