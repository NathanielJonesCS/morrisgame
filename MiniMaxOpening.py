"""White opening minimax, plus the shared recursive search and CLI helpers."""

import sys

from morris import (
    GenerateMovesOpening, GenerateMovesOpeningBlack,
    read_board, write_board, staticEstimationOpening,
)


def _search(board, depth, white_moves, black_moves, evaluation, pruning=False):
    """Search a fixed phase, starting with White/MAX. Return (score, board, count).

    Move generators and evaluation each accept one board string. Generators
    return ordered successor lists; evaluation returns a White-perspective score.
    Depth counts individual moves. Only depth zero and no successors stop search.
    The returned board is an immediate root child (or the unchanged leaf root).
    See PERSON2_HANDOFF.md for the assignment/tournament boundary.
    """
    if not isinstance(board, str) or len(board) != 23 or any(c not in "WBx" for c in board):
        raise ValueError("board must contain exactly 23 characters from W, B, x")
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    if not callable(evaluation):
        raise TypeError("evaluation must be callable")

    positions_evaluated = 0

    def evaluate(position):
        nonlocal positions_evaluated
        positions_evaluated += 1
        return evaluation(position), position

    def visit(position, remaining, maximizing, alpha, beta):
        if remaining == 0:
            return evaluate(position)
        children = white_moves(position) if maximizing else black_moves(position)
        if not children:
            return evaluate(position)

        best_score = float("-inf") if maximizing else float("inf")
        best_board = None
        for child in children:
            score, _ = visit(child, remaining - 1, not maximizing, alpha, beta)
            better = score > best_score if maximizing else score < best_score
            if best_board is None or better:
                best_score = score
                # Keep this node's child, never the descendant returned by visit.
                best_board = child
            if pruning:
                if maximizing:
                    alpha = max(alpha, best_score)
                else:
                    beta = min(beta, best_score)
                if alpha >= beta:
                    break
        return best_score, best_board

    estimate, best_board = visit(board, depth, True, float("-inf"), float("inf"))
    return estimate, best_board, positions_evaluated


def minimax_opening(board, depth, evaluation=staticEstimationOpening):
    """White opening search; return (estimate, immediate best board, leaf count)."""
    return _search(board, depth, GenerateMovesOpening, GenerateMovesOpeningBlack,
                   evaluation)


def _run_cli(search):
    """Shared noninteractive CLI; successful stdout is exactly three lines."""
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} input.txt output.txt depth", file=sys.stderr)
        return 1
    try:
        try:
            depth = int(sys.argv[3])
        except ValueError:
            raise ValueError("depth must be a nonnegative integer") from None
        if depth < 0:
            raise ValueError("depth must be a nonnegative integer")
        board = read_board(sys.argv[1])
        estimate, best_board, count = search(board, depth)
        write_board(sys.argv[2], best_board)
    except (OSError, ValueError, RecursionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Board Position: {best_board}")
    print(f"Positions evaluated by static estimation: {count}")
    print(f"MINIMAX estimate: {estimate}")
    return 0


if __name__ == "__main__":
    sys.exit(_run_cli(minimax_opening))
