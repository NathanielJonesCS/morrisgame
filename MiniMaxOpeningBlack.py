"""
MiniMaxOpeningBlack.py - computes Black's best move in the opening phase.

Usage: python MiniMaxOpeningBlack.py input.txt output.txt depth

Uses the handout's color-swap method:
  1. swap colors in the input board,
  2. compute White's best move on the swapped board (minimax_opening),
  3. swap colors back in the chosen board.
"""
import sys
from morris import read_board, write_board, swap_colors
from MiniMaxOpening import minimax_opening

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python MiniMaxOpeningBlack.py input.txt output.txt depth")
        sys.exit(1)

    board = read_board(sys.argv[1])
    depth = int(sys.argv[3])

    tempb = swap_colors(board)
    estimate, best_board, positions_evaluated = minimax_opening(tempb, depth)
    best_board = swap_colors(best_board)

    write_board(sys.argv[2], best_board)
    print(f"Board Position: {best_board}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}")
    print(f"MINIMAX estimate: {estimate}")