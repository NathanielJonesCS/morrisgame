# morrisgame

CS4346 Morris Game, Variant. Person 1 supplies the shared engine and Black wrappers.
Person 2 supplies White minimax and alpha-beta searches for opening and game play.

See [PERSON2_HANDOFF.md](PERSON2_HANDOFF.md) for commands, evaluator injection,
dependencies, search conventions, and Person 3's remaining integration work.
[Examples.txt](Examples.txt) contains real minimax/alpha-beta comparisons;
[Timing.txt](Timing.txt) records the bounded performance measurements.

```text
python MiniMaxOpening.py examples/opening.txt chosen.txt 3
python ABGame.py examples/midgame.txt chosen.txt 3
python -B -m unittest -v test_search
python -B test_morris.py
python benchmark_search.py --max-depth 6 --timeout 5 --output Timing-local.txt
```

Keep `morris.py` and all four Person 2 search modules together. Confirm shared-file
packaging with the instructor before final submission. Person 3's improved
evaluation and tournament work remain separate responsibilities.
