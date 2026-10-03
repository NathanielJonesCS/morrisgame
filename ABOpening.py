"""Compute White's alpha-beta move in the fixed opening phase."""

import sys

from MiniMaxOpening import _search, _run_cli
from morris import (
    GenerateMovesOpening, GenerateMovesOpeningBlack, staticEstimationOpening,
)


def alphabeta_opening(board, depth, evaluation=staticEstimationOpening):
    """Return (White-perspective estimate, immediate best board, leaf count)."""
    return _search(board, depth, GenerateMovesOpening, GenerateMovesOpeningBlack,
                   evaluation, pruning=True)


if __name__ == "__main__":
    sys.exit(_run_cli(alphabeta_opening))
