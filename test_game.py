

import json
import os
import tempfile
import tkinter as tk
import unittest

from game import NEUTRAL, P1, P2, Board, GameState, PlayerInfo, load_state
from game.constants import PALETTE
from ui.config import GameConfig
from ui.game_view import GameView
from ui.menu import MenuFrame


def napravi_stanje(boje, vlasnici, n, trenutni=P1):

    board = Board(n, 5, PALETTE[:5], boje, vlasnici)
    starts = {P1: 0, P2: n * n - 1}
    players = {}
    for player, start in starts.items():
        region = {i for i in range(n * n) if vlasnici[i] == player}
        players[player] = PlayerInfo(board, start, region)
    return GameState(board, players, trenutni)


def primer_stanja(trenutni=P1):
    
    boje = [0, 1, 2,
            3, 1, 2,
            2, 2, 4]
    vlasnici = [P1, 0, 0,
                0, 0, 0,
                0, 0, P2]
    return napravi_stanje(boje, vlasnici, 3, trenutni)


class TestLogikeIgre(unittest.TestCase):

    def test_nova_igra_pravi_tablu(self):
        stanje = GameState.new(10, 8)
        self.assertEqual(len(stanje.board.colors), 100)
        self.assertTrue(all(0 <= boja < 8 for boja in stanje.board.colors))
        self.assertEqual(stanje.current_player, P1)

    def test_pogresne_dimenzije(self):
        for n, k in [(1, 5), (31, 5), (10, 1), (10, 16)]:
            with self.assertRaises(ValueError):
                GameState.new(n, k)

    def test_pocetni_regioni(self):
      
        for _ in range(100):
            stanje = GameState.new(5, 3)
            p1 = stanje.players[P1]
            p2 = stanje.players[P2]
            self.assertNotEqual(p1.color, p2.color)
            for igrac, info in stanje.players.items():
                self.assertIn(info.start, info.region)
                for i in info.region:
                    self.assertEqual(stanje.board.colors[i], info.color)
                    self.assertEqual(stanje.board.owners[i], igrac)

    def test_susedna_polja(self):
        board = Board.random(3, 3)
        self.assertEqual(sorted(board.neighbors[0]), [1, 3])        
        self.assertEqual(sorted(board.neighbors[4]), [1, 3, 5, 7])  

    def test_legalni_potezi(self):
        self.assertEqual(primer_stanja(P1).legal_moves(), [1, 3])
        self.assertEqual(primer_stanja(P2).legal_moves(), [2])

    def test_provera_poteza(self):
        stanje = primer_stanja()
        self.assertTrue(stanje.is_valid_move(1))
        self.assertFalse(stanje.is_valid_move(0))    
        self.assertFalse(stanje.is_valid_move(4))    
        self.assertFalse(stanje.is_valid_move(99))   
        self.assertFalse(stanje.is_valid_move("1"))  

    def test_igra_nije_gotova(self):
        stanje = primer_stanja()
        self.assertFalse(stanje.is_game_over())
        self.assertIsNone(stanje.winner())

    def test_pobednik(self):
        
        stanje = napravi_stanje([0, 0, 0, 0], [P1, P1, P1, P1], 2)
        self.assertTrue(stanje.is_game_over())
        self.assertEqual(stanje.winner(), P1)

    def test_nereseno(self):
        
        stanje = napravi_stanje([0, 0, 0, 0], [P1, P1, P2, P2], 2)
        self.assertTrue(stanje.is_game_over())
        self.assertEqual(stanje.winner(), NEUTRAL)

    def test_ucitavanje_iz_fajla(self):
        podaci = {
            "palette": {"0": "#E96F50", "1": "#F4CA58"},
            "board": [[[0, P1], [1, NEUTRAL]],
                      [[0, NEUTRAL], [1, P2]]],
            "current_player": P2,
        }
        with tempfile.TemporaryDirectory() as folder:
            putanja = os.path.join(folder, "stanje.json")
            with open(putanja, "w", encoding="utf-8") as f:
                json.dump(podaci, f)
            stanje = load_state(putanja)

        self.assertEqual(stanje.board.n, 2)
        self.assertEqual(stanje.board.k, 2)
        self.assertEqual(stanje.board.colors, [0, 1, 0, 1])
        self.assertEqual(stanje.players[P1].region, {0})
        self.assertEqual(stanje.players[P2].region, {3})
        self.assertEqual(stanje.current_player, P2)


class TestProzora(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw() 

    def tearDown(self):
        self.root.destroy()

    def test_dugme_play_pokrece_igru(self):
        pokrenute = []
        meni = MenuFrame(self.root, on_start=lambda *args: pokrenute.append(args))
        meni._on_play()
        self.assertEqual(len(pokrenute), 1)
        stanje = pokrenute[0][0]
        self.assertEqual((stanje.board.n, stanje.board.k), (10, 8))

    def test_meni_prijavljuje_gresku(self):
        pokrenute = []
        meni = MenuFrame(self.root, on_start=lambda *args: pokrenute.append(args))
        meni.n_var.set("abc")
        meni._on_play()
        self.assertEqual(pokrenute, [])
        self.assertIn("N mora biti ceo broj", meni.error_label.cget("text"))

    def test_prikaz_igre(self):
        prikaz = GameView(self.root, primer_stanja(), GameConfig(3, 5), on_back=lambda: None)
        ukljucena = [boja for boja, dugme in enumerate(prikaz.color_buttons)
                     if dugme.cget("state") == "normal"]
        self.assertEqual(ukljucena, [1, 3])

        prikaz.on_color_chosen(1)
        self.assertIn("Potez je ispravan", prikaz.message_label.cget("text"))


if __name__ == "__main__":
    unittest.main()
