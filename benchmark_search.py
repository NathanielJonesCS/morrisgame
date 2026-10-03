"""Bounded, standard-library alpha-beta timing; Windows-compatible subprocesses."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from ABGame import alphabeta_game
from ABOpening import alphabeta_opening


# Fixed reproducible positions; the two midgame boards appear in the handout.
CASES = {
    "opening_empty": ("opening", "x" * 23),
    "opening_capture": ("opening", "WWxBxxxxxxxxxxxxxxxxxxx"),
    "midgame_handout": ("game", "xxxxxBxWWWWWBBBBxxxxxxx"),
    "midgame_dense": ("game", "WxWWxWWWWWBBBBBBBBxxxxx"),
    "hopping": ("game", "WWxxxWxxxxBBBxxxxxxxxxx"),
}


def run_case(case, depth, timeout):
    """Return one measurement. subprocess.run kills AND waits on timeout.

    Timeout includes interpreter startup; search_seconds measures only search.
    Workers spawn no descendants, so terminating the worker ends the search.
    """
    command = [sys.executable, "-B", str(Path(__file__).resolve()),
               "--worker", case, "--depth", str(depth)]
    start = time.perf_counter()
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=timeout, check=True)
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "wall_seconds": time.perf_counter() - start}
    measurement = json.loads(result.stdout)
    measurement["status"] = "OK"
    measurement["wall_seconds"] = time.perf_counter() - start
    return measurement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=180,
                        help="per-search process timeout in seconds (default: 180)")
    parser.add_argument("--case", choices=CASES, action="append",
                        help="case to run; repeat to select several; default: all")
    parser.add_argument("--output", type=Path, help="also save the report as UTF-8 text")
    parser.add_argument("--worker", choices=CASES, help=argparse.SUPPRESS)
    parser.add_argument("--depth", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.depth is None or args.depth < 0:
            parser.error("worker depth must be nonnegative")
        phase, board = CASES[args.worker]
        search = alphabeta_opening if phase == "opening" else alphabeta_game
        start = time.perf_counter()
        score, chosen, count = search(board, args.depth)
        elapsed = time.perf_counter() - start
        print(json.dumps({"search_seconds": elapsed, "evaluations": count,
                          "estimate": score, "board": chosen}))
        return 0
    if args.max_depth < 2:
        parser.error("--max-depth must be at least 2")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be a positive finite number")

    lines = []
    measurements = []
    def report(line=""):
        lines.append(line)
        print(line, flush=True)

    report("Person 2 alpha-beta search timing (default handout evaluations)")
    report("Measured UTC: " + datetime.now(timezone.utc).isoformat())
    report("Python: " + sys.version.replace("\n", " "))
    report("Platform: " + platform.platform())
    report("Processor: " + (platform.processor() or "not reported"))
    report("Command: python " + subprocess.list2cmdline([Path(__file__).name, *sys.argv[1:]]))
    report(f"Per-process timeout: {args.timeout:g} seconds; one run per case/depth.")
    report("search_s excludes interpreter startup; wall_s includes startup and shutdown.")
    report("TIMEOUT has no completed evaluation count; deeper runs for that case are skipped.")
    for case in args.case or CASES:
        phase, board = CASES[case]
        report()
        report(f"{case}: phase={phase}, board={board}")
        report("depth  status     search_s     wall_s    evaluations")
        for depth in range(2, args.max_depth + 1):
            result = run_case(case, depth, args.timeout)
            measurements.append((case, depth, result))
            if result["status"] == "TIMEOUT":
                report(f"{depth:5}  TIMEOUT           -  {result['wall_seconds']:9.6f}              -")
                break
            report(f"{depth:5}  OK       {result['search_seconds']:10.6f}  "
                   f"{result['wall_seconds']:9.6f}  {result['evaluations']:13}")
    report()
    completed_maxima = []
    for case in args.case or CASES:
        completed = [depth for name, depth, result in measurements
                     if name == case and result["status"] == "OK"]
        completed_maxima.append(max(completed, default=0))
        report(f"{case}: completed depths {', '.join(map(str, completed)) or 'none'}.")
    report("Deepest completed depths are tested depths, not proven maximum depths.")
    report("Measure on the tournament computer; Person 3's improved evaluator can change runtime.")
    report("These boards do not guarantee a runtime bound for every position.")
    report("The four-minute response limit includes operating and posting the move.")
    report("Use --timeout 180 for a longer local study, leaving operational room.")
    if min(completed_maxima) >= 2:
        starting_depth = min(3, min(completed_maxima))
        report(f"Conservative starting point: depth {starting_depth} completed for every selected case.")
        report("Treat this as a starting point for local testing, not a guaranteed tournament depth.")
    else:
        report("No common starting depth established: at least one case did not complete depth 2.")
    if args.output:
        args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Benchmark error: {error}", file=sys.stderr)
        sys.exit(1)
