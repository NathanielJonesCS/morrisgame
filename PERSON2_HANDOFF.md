# Person 2: search implementation and handoff

Person 2 implements the four White search programs, reusable evaluator injection,
search tests, real comparison examples, and bounded timing. Person 1's `morris.py`,
Black wrappers, and engine tests are unchanged. Person 3's programs are not implemented.
All delivered Python code uses only the standard library.

## Files and dependencies

| File | Purpose / imports needed at runtime |
| --- | --- |
| `MiniMaxOpening.py` | Opening minimax; owns the shared `_search` and `_run_cli`; imports `morris.py` |
| `MiniMaxGame.py` | Midgame/endgame minimax; imports `MiniMaxOpening.py` and `morris.py` |
| `ABOpening.py` | Opening alpha-beta; imports `MiniMaxOpening.py` and `morris.py` |
| `ABGame.py` | Midgame/endgame alpha-beta; imports `MiniMaxOpening.py` and `morris.py` |
| `test_search.py` | Assertions, controlled trees, engine integration, CLI and benchmark tests |
| `benchmark_search.py` | Separate subprocess timing for five fixed boards; imports both AB programs |
| `Examples.txt`, `examples/opening.txt`, `examples/midgame.txt` | Actual comparison outputs and reproducible inputs |
| `Timing.txt` | Actual bounded benchmark results and limitations |
| `PERSON2_HANDOFF.md`, README addition | Usage, conventions, and integration guidance |

Give Person 3 all four search modules and Person 1's `morris.py` in one directory,
along with this handoff, tests, examples, and timing utility. The Black wrappers
add their existing imports from `MiniMaxOpening.py` / `MiniMaxGame.py`.
These programs require shared modules; they are **not standalone files**.

## Commands

Run from the project directory with Python 3:

```text
python MiniMaxOpening.py examples/opening.txt chosen_minimax.txt 3
python ABOpening.py examples/opening.txt chosen_ab.txt 3
python MiniMaxGame.py examples/midgame.txt chosen_minimax.txt 3
python ABGame.py examples/midgame.txt chosen_ab.txt 3
python MiniMaxOpeningBlack.py examples/opening.txt chosen_black.txt 2
python MiniMaxGameBlack.py examples/midgame.txt chosen_black.txt 2
python -B -m unittest -v test_search
python -B test_morris.py
python benchmark_search.py --max-depth 6 --timeout 5 --output Timing-local.txt
python benchmark_search.py --max-depth 8 --timeout 180 --output Timing-tournament-PC.txt
```

The first four commands reproduce the outputs recorded in `Examples.txt`.
The chosen files are overwritten by later commands. Compare each pair before
moving to the next phase. Each successful program prints exactly three lines:
board, static evaluation count, and `MINIMAX estimate`. The output file contains
only the 23-character board. Errors in the four White CLIs go to stderr with a
nonzero exit status. Imports run no CLI and produce no output.

The test suite also reruns each example and checks its output against the report.
It runs both unchanged Black wrappers. Person 1's checks are sanity checks rather
than a complete independent verification of game rules; because some only print
`FAIL`, the new suite also checks their output for failure text.

## Person 3's callable interfaces

```python
from MiniMaxOpening import minimax_opening
from MiniMaxGame import minimax_game
from ABOpening import alphabeta_opening
from ABGame import alphabeta_game

# Supply your own callables; their definitions belong to Person 3.
result = minimax_opening(board, depth, evaluation=my_opening_evaluation)
result = minimax_game(board, depth, evaluation=my_game_evaluation)
result = alphabeta_opening(board, depth, evaluation=my_opening_evaluation)
result = alphabeta_game(board, depth, evaluation=my_game_evaluation)
estimate, best_board, positions_evaluated = result
```

All four also accept just `(board, depth)`. Opening defaults to
`staticEstimationOpening`; game defaults to `staticEstimationMidgameEndgame`.

- `board`: a string of exactly 23 characters from `W`, `B`, `x`, using Person 1's mapping.
- `depth`: a nonnegative integer counting individual moves (plies). Depth three
  means White move, Black reply, White move, then evaluation.
- `evaluation`: callable accepting one board string, returning a numeric score
  from White's perspective. Use finite scores; NaN is not an ordered score.
  It should evaluate features, without doing its own recursive search.
- Return order: `(estimate, best_board, positions_evaluated)`. The estimate is
  the backed-up score. `best_board` is the immediate root successor, not a leaf.
  The integer count is the number of actual evaluation calls during this search.

White always moves first in these interfaces and maximizes. Black replies minimize.
Every leaf uses the supplied evaluator. Each call has its own local counter.
Generated nodes, move-generation calls inside an evaluator, and pruned branches
do not increment the count.

Children retain the engine's order. Equal values keep the first move; choices
change only on a strictly better score. Alpha-beta starts with negative/positive
infinity, updates alpha at MAX and beta at MIN, and cuts off when alpha >= beta.
Both algorithms use identical depth, evaluation, move order, and stopping rules.

### Depth zero, no successors, and fixed phase

Depth zero evaluates once and returns the input unchanged: **it does not select
a new move**. At any earlier node with no successors, search evaluates that board
once. If that node is the root, the input board is returned unchanged.

The assignment specifies handout evaluators but does not explicitly require a
separate early game-over test inside recursion. Adopted convention: stop only
at depth zero or when the current player's generator returns no successors.
There is no separate piece-count stop, invented win/loss score, or stop based
on an evaluator returning +/-10000. This also ensures evaluator injection is
used on every evaluated leaf. The same convention applies to both algorithms.

Each wrapper fixes its phase for the entire tree. Opening never switches to
movement based on the number of pieces; game searches use Person 1's movement
generator, including automatic hopping at exactly three pieces.

### Shared internal helper

Person 3 normally needs only the four public functions. For understanding the
implementation, `_search(board, depth, white_moves, black_moves, evaluation,
pruning=False)` is the private common core in `MiniMaxOpening.py`. Its first two
arguments have the meanings above. `white_moves` and `black_moves` accept a board
and return an ordered list of successor strings for their respective sides.
`evaluation` is the leaf callback; `pruning` enables alpha-beta when true and
ordinary minimax when false. The root is always White/MAX and turns alternate.
Its return order is the same tuple. It has no terminal callback or phase callback.

### Black through color swapping

Person 1's wrappers swap the board, call White minimax, and swap the chosen board
back. Their reported estimate is left in the **swapped-board perspective**.
The same method supports alpha-beta:

```python
from morris import swap_colors
from ABGame import alphabeta_game

estimate, swapped_choice, count = alphabeta_game(
    swap_colors(board), depth, evaluation=my_game_evaluation
)
black_choice = swap_colors(swapped_choice)
```

For opening, substitute `alphabeta_opening` and the opening evaluator. In this
call the evaluator's White pieces represent the original Black player, so a
larger returned score favors original Black. Do not automatically negate or
reinterpret the existing wrappers' output. Negating a swapped score need not
reproduce the original White evaluator, since the handout evaluator is asymmetric.

## Results and timing

Final verification: all 20 `unittest` tests passed in 9.885 seconds. This includes
all four White CLIs, both unchanged Black wrappers, report reproduction, and
benchmark timeout recovery. The separate engine run printed `tables OK` and all
10 sanity checks passed. Syntax/whitespace checks passed; no cache or temporary
benchmark files remain in the deliverable set. No branches or commits were changed.

At depth three, the opening example selects `WWWxxxxxxxxxxxxxxxxxxxx`, score 3:
minimax evaluates 7,256 leaves; alpha-beta evaluates 382 (94.74% fewer).
The midgame example selects `WxxxxBxWxWWWBBBBxxxxxxx`, score 991:
minimax evaluates 677 leaves; alpha-beta evaluates 233 (65.58% fewer).

The recorded Windows/Python 3.14.3 benchmark tested depths 2 through 6 with a
five-second process limit. Both opening boards and both ordinary midgame boards
completed depth six (search times 0.759 to 4.616 seconds). Hopping completed
depth three in 1.095 seconds; depth four timed out and higher depths were skipped.
See `Timing.txt` for every board, count, time, platform, and the exact command.

Depth three is a conservative **starting point for further testing** across these
cases. It is not a universal safe tournament depth. Depth six is the deepest
completed depth for four boards, not a proven maximum. Re-run on the tournament
computer with Person 3's improved evaluator. Different boards and evaluation
costs can change runtime substantially. One measurement per board/depth does not
establish a worst-case bound. The four-minute response window also includes
operating the program and posting the response.

The benchmark uses `time.perf_counter()`. Each search runs in a separate Python
process. A timeout includes startup; completed search timing excludes it. On a
timeout, `subprocess.run` kills and waits for that worker, and the parent skips
deeper runs for that case. The default limit is 180 seconds. No partial leaf
count is claimed for a timed-out search. `--case hopping` (or another case name
from `--help`) selects a case; repeat `--case` to select several.

## Person 3's remaining responsibilities

Person 3 owns improved evaluations, `MiniMaxOpeningImproved.py`,
`MiniMaxGameImproved.py`, `MyStaticEstimation.txt`, `TournamentAgent.py`, and
tournament coordination. The improved wrappers can call the public interfaces
above without copying recursion. Add improved-evaluation examples to the team's
materials and remeasure performance.

A phase-specific assignment search is not a complete tournament agent:

- Track placements explicitly. Opening lasts 18 individual placement moves;
  captures mean the board alone cannot reliably identify when opening ends.
- Near placement 18, either cap opening depth at the remaining placement count
  or implement an explicit phase-transition policy for tournament search.
- Own terminal handling appropriate to tournament play, including the side
  unable to move and repetition with the same side to move. The handout evaluator
  does not score all terminal situations symmetrically: it checks Black mobility
  but not White mobility, and gives Black <= 2 pieces priority if both are <= 2.
- Handle unchanged-board results at depth zero or a no-move root; these are not
  instructions to post an illegal pass. Choose depth/time policy and test both colors.

## Explaining the search in class

Minimax asks which move gives White the best outcome assuming Black replies as
strongly as possible. Each leaf receives a static score. White takes the largest
child score because positive scores favor White; Black takes the smallest because
that hurts White. These choices back up through the tree to the root.

Alpha is the best score MAX can already secure along the current search path;
beta is the best upper limit MIN can already enforce. When alpha reaches beta,
further children cannot make that branch improve the ancestor's decision, so
alpha-beta skips them. Keeping the same child order and the first tied choice
preserves the root move as well as the score. A cutoff result can be a bound;
it need not be an exact score for the skipped subtree.

The program must make one move now. That is why each level remembers its direct
child, even when a deeper recursive call supplied the score. The evaluation count
measures how many boards actually reached the evaluator, not how many boards
were generated. It makes the pruning savings visible.

## Sources, interpretation, and packaging checks

No applicable `AGENTS.md` was found in the project or its ancestor directories.
The initial working tree was clean. Inspected all five Person 1 files before edits.
Local source documents read:

- `C:/Users/kylek/Downloads/Morris-Variant.pdf`, all five pages: board mapping,
  fixed-phase generators, color swapping, removal fallback (page 4), and estimates
  (page 5). The no-capture fallback when all opposing pieces are in mills agrees
  with Person 1. No engine change was required for this work.
- `C:/Users/kylek/Downloads/Project.pdf` (also present as `Project (1).pdf`): the
  CS4346 Morris AI Tournament assignment, including output, comparisons, 18
  placements, four-minute limit, and required submission filenames.

Files named `MorrisProject.pdf` and `Morris_Team_Tasks.pdf` were not found in the
project, school Desktop tree, Downloads, Documents, or attachments search. The
local `Project.pdf` supplies the instructor assignment; ownership and team-sheet
integration requirements follow the user's supplied request.

The submission list does not explicitly settle whether extra shared helpers
such as `morris.py` may accompany the required files. Confirm this with the
instructor before packaging; the user reports this team question is still open.
Keep `morris.py` and the documented imports together during development. No
standalone-file compliance is claimed. The early-stopping convention above is
documented for review if the instructor or missing team sheet specifies another.
