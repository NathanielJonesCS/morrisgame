"""Person 2 regression tests: python -m unittest -v test_search."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import ABGame
import ABOpening
import MiniMaxGame
import MiniMaxOpening
import morris


ROOT = Path(__file__).resolve().parent
OPENING = "WWxBxxxxxxxxxxxxxxxxxxx"
MIDGAME = "xxxxxBxWWWWWBBBBxxxxxxx"
DENSE = "WxWWxWWWWWBBBBBBBBxxxxx"
HOPPING = "WWxxxWxxxxBBBxxxxxxxxxx"
SEARCHES = (
    (MiniMaxOpening, MiniMaxOpening.minimax_opening, morris.GenerateMovesOpening,
     morris.staticEstimationOpening, "GenerateMovesOpening", "GenerateMovesOpeningBlack"),
    (ABOpening, ABOpening.alphabeta_opening, morris.GenerateMovesOpening,
     morris.staticEstimationOpening, "GenerateMovesOpening", "GenerateMovesOpeningBlack"),
    (MiniMaxGame, MiniMaxGame.minimax_game, morris.GenerateMovesMidgameEndgame,
     morris.staticEstimationMidgameEndgame, "GenerateMovesMidgameEndgame",
     "GenerateMovesMidgameEndgameBlack"),
    (ABGame, ABGame.alphabeta_game, morris.GenerateMovesMidgameEndgame,
     morris.staticEstimationMidgameEndgame, "GenerateMovesMidgameEndgame",
     "GenerateMovesMidgameEndgameBlack"),
)


def node(number):
    """Unique valid board strings for the independently specified synthetic tree."""
    return format(number, "023b").translate(str.maketrans("01", "xW"))


class SearchTests(unittest.TestCase):
    def test_depth_zero(self):
        for _, search, _, evaluation, _, _ in SEARCHES:
            with self.subTest(search=search.__name__):
                self.assertEqual(search(MIDGAME, 0), (evaluation(MIDGAME), MIDGAME, 1))

    def test_one_move_independent_maximum_and_legality(self):
        for _, search, generate, evaluate, _, _ in SEARCHES:
            board = OPENING if "opening" in search.__name__ else MIDGAME
            children = generate(board)
            scores = [evaluate(child) for child in children]
            expected_score = max(scores)
            expected_board = children[scores.index(expected_score)]
            with self.subTest(search=search.__name__):
                self.assertEqual(search(board, 1), (expected_score, expected_board, len(children)))

    def test_independent_three_ply_tree_and_pruning_count(self):
        # MAX(root): MIN(A: MAX(3,5), MAX(6,9)), MIN(B: MAX(2,4), MAX(7,8)).
        # A backs up min(5,9)=5; B backs up min(4,8)=4. Root chooses A.
        # AB skips 9 after seeing 6 >= beta 5, then skips B's (7,8) subtree.
        white = {node(0): [node(1), node(2)],
                 node(3): [node(7), node(8)], node(4): [node(9), node(10)],
                 node(5): [node(11), node(12)], node(6): [node(13), node(14)]}
        black = {node(1): [node(3), node(4)], node(2): [node(5), node(6)]}
        values = dict(zip((node(i) for i in range(7, 15)), [3, 5, 6, 9, 2, 4, 7, 8]))
        for module, search, _, _, white_name, black_name in SEARCHES:
            visited = []
            def evaluate(board):
                visited.append(board)
                return values[board]
            with self.subTest(search=search.__name__), \
                    patch.object(module, white_name, side_effect=lambda b: white[b]), \
                    patch.object(module, black_name, side_effect=lambda b: black[b]):
                expected_count = 5 if "alphabeta" in search.__name__ else 8
                self.assertEqual(search(node(0), 3, evaluate), (5, node(1), expected_count))
                expected_leaves = [7, 8, 9, 11, 12] if expected_count == 5 else list(range(7, 15))
                self.assertEqual(visited, [node(i) for i in expected_leaves])

    def test_equal_bound_keeps_first_root_move(self):
        # B returns an upper bound of 5 after pruning its 0; it must not replace A.
        white = {node(0): [node(1), node(2), node(3)]}
        black = {node(1): [node(4), node(5)], node(2): [node(6), node(7)],
                 node(3): [node(8), node(9)]}
        values = dict(zip((node(i) for i in range(4, 10)), [5, 6, 5, 0, 4, 9]))
        for module, search, _, _, wn, bn in SEARCHES:
            with self.subTest(search=search.__name__), \
                    patch.object(module, wn, side_effect=lambda b: white[b]), \
                    patch.object(module, bn, side_effect=lambda b: black[b]):
                count = 4 if "alphabeta" in search.__name__ else 6
                self.assertEqual(search(node(0), 2, values.__getitem__), (5, node(1), count))

    def test_all_equal_scores_keep_first(self):
        for _, search, generate, _, _, _ in SEARCHES:
            with self.subTest(search=search.__name__):
                self.assertEqual(search(MIDGAME, 2, lambda b: 7)[:2],
                                 (7, generate(MIDGAME)[0]))

    def test_equivalence_across_phases_and_depths(self):
        cases = [(MiniMaxOpening.minimax_opening, ABOpening.alphabeta_opening,
                  ["x" * 23, OPENING]),
                 (MiniMaxGame.minimax_game, ABGame.alphabeta_game,
                  [MIDGAME, DENSE, HOPPING])]
        for minimax, alphabeta, boards in cases:
            for board in boards:
                # Hopping's unpruned depth-three tree is much more expensive;
                # cover depths 0..2 here and deeper alpha-beta in the benchmark.
                for depth in range(3 if board == HOPPING else 4):
                    with self.subTest(board=board, depth=depth, phase=minimax.__name__):
                        plain = minimax(board, depth)
                        pruned = alphabeta(board, depth)
                        self.assertEqual(plain[:2], pruned[:2])
                        self.assertLessEqual(pruned[2], plain[2])

    def test_opening_capture_and_all_in_mills_variant(self):
        for search in [MiniMaxOpening.minimax_opening, ABOpening.alphabeta_opening]:
            isolated = "xWW" + "x" * 18 + "B" + "x"
            self.assertEqual(search(isolated, 1)[:2], (3, "WWW" + "x" * 20))
            protected = "xWW" + "x" * 17 + "BBB"
            result = search(protected, 1)
            self.assertEqual(result[:2], (0, "WWW" + "x" * 17 + "BBB"))
            self.assertIn(result[1], morris.GenerateMovesOpening(protected))

    def test_game_mill_capture(self):
        board = morris.set_pieces("x" * 23, [(1, "W"), (2, "W"), (3, "W"),
                                              (15, "W"), (8, "B"), (11, "B"),
                                              (18, "B"), (22, "B")])
        for search in [MiniMaxGame.minimax_game, ABGame.alphabeta_game]:
            result = search(board, 1)
            self.assertIn(result[1], morris.GenerateMovesMidgameEndgame(board))
            self.assertEqual(result[1].count("B"), 3)
            self.assertTrue(any(morris.closeMill(i, result[1]) for i, c in enumerate(result[1]) if c == "W"))

    def test_no_successor_at_root(self):
        board = "W" * 12 + "B" * 11
        for _, search, _, evaluation, _, _ in SEARCHES:
            with self.subTest(search=search.__name__):
                self.assertEqual(search(board, 3), (evaluation(board), board, 1))

    def test_no_successor_at_internal_node_uses_custom_evaluation(self):
        for module, search, _, _, wn, bn in SEARCHES:
            with self.subTest(search=search.__name__), \
                    patch.object(module, wn, return_value=[node(1)]), \
                    patch.object(module, bn, return_value=[]):
                self.assertEqual(search(node(0), 3, lambda b: 42), (42, node(1), 1))

    def test_custom_evaluator_actual_calls_and_repeated_searches(self):
        for _, search, _, _, _, _ in SEARCHES:
            calls = []
            def evaluate(board):
                calls.append(board)
                return 2.5
            first = search(MIDGAME, 2, evaluation=evaluate)
            self.assertEqual(first[0], 2.5)
            self.assertEqual(first[2], len(calls))
            calls.clear()
            self.assertEqual(search(MIDGAME, 2, evaluation=evaluate), first)
            self.assertEqual(first[2], len(calls))
            calls.clear()
            self.assertEqual(search(MIDGAME, 0, evaluation=evaluate), (2.5, MIDGAME, 1))
            self.assertEqual(calls, [MIDGAME])

    def test_no_implicit_piece_count_terminal_stop(self):
        board = "WW" + "x" * 19 + "BB"
        for search in [MiniMaxGame.minimax_game, ABGame.alphabeta_game]:
            result = search(board, 1)
            self.assertEqual(result[0], 10000)
            self.assertEqual(result[2], len(morris.GenerateMovesMidgameEndgame(board)))
            self.assertNotEqual(result[1], board)

    def test_public_input_validation(self):
        for _, search, _, _, _, _ in SEARCHES:
            for board in ["x" * 22, "x" * 24, "?" * 23, ["x"] * 23, None]:
                with self.assertRaises(ValueError):
                    search(board, 0)
            for depth in [-1, 1.5, "2", True]:
                with self.assertRaises(ValueError):
                    search(MIDGAME, depth)


class CLITests(unittest.TestCase):
    def run_program(self, program, *args):
        return subprocess.run([sys.executable, "-B", str(ROOT / program), *map(str, args)],
                              capture_output=True, text=True, timeout=20)

    def check_success(self, result, output, expected):
        score, board, count = expected
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.splitlines(), [
            f"Board Position: {board}",
            f"Positions evaluated by static estimation: {count}",
            f"MINIMAX estimate: {score}"])
        self.assertEqual(output.read_text(), board)

    def test_all_four_success_and_depth_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "input.txt", Path(directory) / "output.txt"
            for module, search, _, _, _, _ in SEARCHES:
                board = OPENING if "opening" in search.__name__ else MIDGAME
                source.write_text(board)
                for depth in [0, 2]:
                    with self.subTest(program=module.__name__, depth=depth):
                        result = self.run_program(module.__name__ + ".py", source, output, depth)
                        self.check_success(result, output, search(board, depth))

    def test_cli_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "input.txt", Path(directory) / "output.txt"
            for module, *_ in SEARCHES:
                program = module.__name__ + ".py"
                source.write_text(MIDGAME)
                failures = [(), (source, output, "-1"), (source, output, "1.5"),
                            (source, output, "oops"), (Path(directory) / "missing", output, 0),
                            (source, directory, 0)]
                for args in failures:
                    result = self.run_program(program, *args)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertTrue(result.stderr.strip())
                for malformed in ["x" * 22, "x" * 24, "?" * 23, ""]:
                    source.write_text(malformed)
                    result = self.run_program(program, source, output, 1)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("Invalid board", result.stderr)

    def test_unchanged_black_wrappers(self):
        cases = [("MiniMaxOpeningBlack.py", MiniMaxOpening.minimax_opening,
                  morris.GenerateMovesOpeningBlack, OPENING),
                 ("MiniMaxGameBlack.py", MiniMaxGame.minimax_game,
                  morris.GenerateMovesMidgameEndgameBlack, MIDGAME)]
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "input.txt", Path(directory) / "output.txt"
            for program, search, generate, board in cases:
                source.write_text(board)
                score, chosen, count = search(morris.swap_colors(board), 2)
                chosen = morris.swap_colors(chosen)
                self.assertIn(chosen, generate(board))
                self.check_success(self.run_program(program, source, output, 2),
                                   output, (score, chosen, count))

    def test_imports_have_no_cli_side_effects(self):
        code = ("import sys; sys.argv = ['ignored', 'bad', 'args']; "
                "import MiniMaxOpening, MiniMaxGame, ABOpening, ABGame; "
                "import MiniMaxOpeningBlack, MiniMaxGameBlack")
        result = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_existing_engine_checks_report_no_failure(self):
        # Person 1's check() prints FAIL without raising, so inspect stdout too.
        result = self.run_program("test_morris.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("FAIL", result.stdout)
        self.assertIn("tables OK", result.stdout)

    def test_recorded_examples_match_actual_cli_output(self):
        report = (ROOT / "Examples.txt").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "chosen.txt"
            for module, *_ in SEARCHES:
                source = ROOT / "examples" / ("opening.txt" if "Opening" in module.__name__ else "midgame.txt")
                result = self.run_program(module.__name__ + ".py", source, output, 3)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(result.stdout.strip(), report)

    def test_benchmark_completed_run_and_timeout_stop(self):
        result = self.run_program("benchmark_search.py", "--case", "opening_empty",
                                  "--max-depth", 2, "--timeout", 10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("opening_empty: completed depths 2.", result.stdout)
        # A real process timeout also verifies recovery and skipping deeper runs.
        result = self.run_program("benchmark_search.py", "--case", "opening_empty",
                                  "--max-depth", 5, "--timeout", 0.001)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("    2  TIMEOUT", result.stdout)
        self.assertNotIn("    3  ", result.stdout)
        self.assertIn("opening_empty: completed depths none.", result.stdout)


if __name__ == "__main__":
    unittest.main()
