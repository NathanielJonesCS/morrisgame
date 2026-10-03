"""Compute White's minimax move in the fixed midgame/endgame phase."""

import sys

from MiniMaxOpening import _search, _run_cli
from morris import (
    GenerateMovesMidgameEndgame, GenerateMovesMidgameEndgameBlack,
    staticEstimationMidgameEndgame,
)


def minimax_game(board, depth, evaluation=staticEstimationMidgameEndgame):
    """Return (White-perspective estimate, immediate best board, leaf count)."""
    return _search(board, depth, GenerateMovesMidgameEndgame,
                   GenerateMovesMidgameEndgameBlack, evaluation)


if __name__ == "__main__":
    sys.exit(_run_cli(minimax_game))
