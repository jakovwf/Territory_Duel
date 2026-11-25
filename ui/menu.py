import tkinter as tk
from tkinter import filedialog
from typing import Callable, Optional

from game.constants import MAX_K, MAX_N, MIN_K, MIN_N, P1, P2
from game.serialization import load_state
from game.state import GameState
from ui.config import HUMAN_VS_COMPUTER, HUMAN_VS_HUMAN, GameConfig

# on_start(state, config, from_file)
StartCallback = Callable[[GameState, GameConfig, bool], None]


class MenuFrame(tk.Frame):
    """Pocetni meni: izbor rezima, ko igra prvi, N i K."""

    def __init__(self, master: tk.Misc, on_start: StartCallback) -> None:
        super().__init__(master, padx=20, pady=20)
        self.on_start = on_start

        self.mode_var = tk.StringVar(value=HUMAN_VS_HUMAN)
        self.first_var = tk.StringVar(value="human")     # "human" / "computer"
        self.human_as_var = tk.IntVar(value=P1)          # za koga igra covek
        self.hh_first_var = tk.IntVar(value=P1)          # prvi u rezimu dva igraca
        self.n_var = tk.StringVar(value="10")
        self.k_var = tk.StringVar(value="8")

        self._build()
        self._update_mode_options()

    def _build(self) -> None:
        tk.Label(self, text="Borba za teritoriju", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        # izbor rezima
        mode_box = tk.LabelFrame(self, text="Režim", padx=10, pady=5)
        mode_box.pack(fill="x", pady=5)
        tk.Radiobutton(mode_box, text="Dva igrača", variable=self.mode_var,
                       value=HUMAN_VS_HUMAN, command=self._update_mode_options).pack(anchor="w")
        tk.Radiobutton(mode_box, text="Igrač protiv računara", variable=self.mode_var,
                       value=HUMAN_VS_COMPUTER, command=self._update_mode_options).pack(anchor="w")

        # kontejner za opcije koje zavise od rezima
        self.options_box = tk.Frame(self)
        self.options_box.pack(fill="x")

        # opcije za dva igraca
        self.hh_frame = tk.LabelFrame(self.options_box, text="Prvi igra", padx=10, pady=5)
        tk.Radiobutton(self.hh_frame, text="P1", variable=self.hh_first_var, value=P1).pack(side="left")
        tk.Radiobutton(self.hh_frame, text="P2", variable=self.hh_first_var, value=P2).pack(side="left")

        # opcije za igru protiv racunara
        self.hc_frame = tk.Frame(self.options_box)
        first_box = tk.LabelFrame(self.hc_frame, text="Ko igra prvi", padx=10, pady=5)
        first_box.pack(fill="x", pady=5)
        tk.Radiobutton(first_box, text="Čovek", variable=self.first_var, value="human").pack(side="left")
        tk.Radiobutton(first_box, text="Računar", variable=self.first_var, value="computer").pack(side="left")
        as_box = tk.LabelFrame(self.hc_frame, text="Čovek igra kao", padx=10, pady=5)
        as_box.pack(fill="x", pady=5)
        tk.Radiobutton(as_box, text="P1", variable=self.human_as_var, value=P1).pack(side="left")
        tk.Radiobutton(as_box, text="P2", variable=self.human_as_var, value=P2).pack(side="left")

        # unos N i K
        size_box = tk.LabelFrame(self, text="Tabla", padx=10, pady=5)
        size_box.pack(fill="x", pady=5)
        tk.Label(size_box, text=f"N ({MIN_N}-{MAX_N}):").grid(row=0, column=0, sticky="w")
        tk.Spinbox(size_box, from_=MIN_N, to=MAX_N, textvariable=self.n_var, width=5).grid(row=0, column=1, padx=5)
        tk.Label(size_box, text=f"K ({MIN_K}-{MAX_K}):").grid(row=1, column=0, sticky="w")
        tk.Spinbox(size_box, from_=MIN_K, to=MAX_K, textvariable=self.k_var, width=5).grid(row=1, column=1, padx=5)

        tk.Button(self, text="Play", width=25, command=self._on_play).pack(pady=(10, 3))
        tk.Button(self, text="Učitaj stanje iz fajla", width=25, command=self._on_load).pack(pady=3)

        # poruka o gresci (umesto iskacucih prozora)
        self.error_label = tk.Label(self, text="", fg="red", wraplength=300, justify="left")
        self.error_label.pack(pady=5)

    def _update_mode_options(self) -> None:
        # prikazuje samo opcije za izabrani rezim
        self.hh_frame.pack_forget()
        self.hc_frame.pack_forget()
        if self.mode_var.get() == HUMAN_VS_COMPUTER:
            self.hc_frame.pack(fill="x")
        else:
            self.hh_frame.pack(fill="x", pady=5)

    def _show_error(self, text: str) -> None:
        self.error_label.config(text=text)

    def _read_int(self, var: tk.StringVar, name: str, low: int, high: int) -> Optional[int]:
        # cita ceo broj iz polja i proverava opseg, vraca None pri gresci
        try:
            value = int(var.get().strip())
        except ValueError:
            self._show_error(f"{name} mora biti ceo broj.")
            return None
        if not low <= value <= high:
            self._show_error(f"{name} mora biti od {low} do {high}.")
            return None
        return value

    def _make_config(self, n: int, k: int) -> GameConfig:
        # pravi konfiguraciju iz izabranih opcija
        if self.mode_var.get() == HUMAN_VS_COMPUTER:
            human = self.human_as_var.get()
            computer = P2 if human == P1 else P1
            first = human if self.first_var.get() == "human" else computer
            return GameConfig(n, k, HUMAN_VS_COMPUTER, first, computer)
        return GameConfig(n, k, HUMAN_VS_HUMAN, self.hh_first_var.get(), None)

    def _on_play(self) -> None:
        n = self._read_int(self.n_var, "N", MIN_N, MAX_N)
        if n is None:
            return
        k = self._read_int(self.k_var, "K", MIN_K, MAX_K)
        if k is None:
            return
        config = self._make_config(n, k)
        try:
            state = GameState.new(n, k, first_player=config.first_player)
        except ValueError as e:
            self._show_error(str(e))
            return
        self._show_error("")
        self.on_start(state, config, False)

    def _on_load(self) -> None:
        path = filedialog.askopenfilename(
            title="Učitaj stanje",
            filetypes=[("JSON fajlovi", "*.json"), ("Svi fajlovi", "*.*")])
        if not path:
            return  # korisnik je odustao
        self.load_from_path(path)

    def load_from_path(self, path: str) -> None:
        # ucitava stanje iz fajla; n i k se uzimaju iz stanja
        try:
            state = load_state(path)
        except Exception as e:  # los fajl, los JSON, nedostaju kljucevi...
            self._show_error(f"Greška pri učitavanju: {e}")
            return
        config = self._make_config(state.board.n, state.board.k)
        config.first_player = state.current_player
        self._show_error("")
        self.on_start(state, config, True)
