"""White opening minimax, plus the shared recursive search and CLI helpers."""

import sys

from cli_helper import (
            _search,
            _run_cli
)

from morris import (
            GenerateMovesOpening, 
            GenerateMovesOpeningBlack,
            read_board, 
            write_board, 
            staticEstimationOpening,
)

def minimax_opening(board, depth, evaluation=staticEstimationOpening):
    """White opening search; return (estimate, immediate best board, leaf count)."""
    return _search(board, depth, GenerateMovesOpening, GenerateMovesOpeningBlack, evaluation)

if __name__ == "__main__":
    sys.exit(_run_cli(minimax_opening))
