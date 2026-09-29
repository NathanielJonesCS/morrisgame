"""test_morris.py - sanity checks for morris.py. Run: python test_morris.py"""
from morris import *

# Tables: adjacency is symmetric and every mill is a connected line
for j in range(23):
    for k in NEIGHBORS[j]:
        assert j in NEIGHBORS[k], f"{j}->{k} not symmetric"
for a, b, c in MILLS:
    assert b in NEIGHBORS[a] and c in NEIGHBORS[b], f"mill {a, b, c} not a line"
assert MILLS_AT[0] == [(1, 2), (8, 20), (3, 6)]   # handout case j==0
assert MILLS_AT[1] == [(0, 2)]                     # handout case j==1
print("tables OK")

def check(name, got, expected):
    status = "PASS" if got == expected else "FAIL"
    print(f"{status}  {name}: got {got}, expected {expected}")

# 1: empty board -> 23 placements
check("empty board adds", len(GenerateAdd("x" * 23)), 23)

# 2: placing at a0 closes a0-d0-g0 and removes the isolated B at d6
b2 = "xWW" + "x" * 18 + "B" + "x"
L2 = GenerateAdd(b2)
check("mill + removal count", len(L2), 20)
check("removal board present", "WWW" + "x" * 20 in L2, True)

# 3: same mill, but all B are in the a6-d6-g6 mill -> nothing removed
b3 = "xWW" + "x" * 17 + "BBB"
L3 = GenerateAdd(b3)
check("all-in-mill fallback count", len(L3), 18)
check("fallback board present", "WWW" + "x" * 17 + "BBB" in L3, True)

# 4: White has 3 pieces -> hopping
b4 = "WWxxxW" + "xxxx" + "BBB" + "x" * 10
check("hopping count", len(GenerateMovesMidgameEndgame(b4)), 53)

# 5: Black generator on an empty board
L5 = GenerateMovesOpeningBlack("x" * 23)
check("black opening", (len(L5), all(p.count('B') == 1 and 'W' not in p for p in L5)), (23, True))

# 6: static estimation opening
check("opening estimate", staticEstimationOpening("WWxBxxxxxxxxxxxxxxxxxxx"), 1)

# 7: static estimation midgame, Black at 2 pieces -> White wins
check("black <= 2 pieces", staticEstimationMidgameEndgame("WWWxxxxxxxxxxxxxxxxxxBB"), 10000)

# 8: static estimation midgame, handout example board
b8 = "xxxxxBxWWWWWBBBBxxxxxxx"
expected8 = 1000 * (5 - 5) - len(GenerateMovesMidgameEndgameBlack(b8))
check("handout board estimate", staticEstimationMidgameEndgame(b8), expected8)