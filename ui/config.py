from dataclasses import dataclass
from typing import Optional

from game.constants import P1

HUMAN_VS_HUMAN = "human_vs_human"
HUMAN_VS_COMPUTER = "human_vs_computer"


@dataclass
class GameConfig:
    """Podesavanja partije koja se biraju u meniju."""
    n: int
    k: int
    mode: str = HUMAN_VS_HUMAN
    first_player: int = P1                 # ko igra prvi potez (P1 ili P2)
    computer_player: Optional[int] = None  # P1, P2 ili None (dva igraca)

    def is_computer(self, player: int) -> bool:
        # da li datog igraca vodi racunar
        return self.computer_player is not None and self.computer_player == player
