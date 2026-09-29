"""
morris.py - Game engine for the Morris Game, Variant (CS4346).


A board is a 23-character string of 'W', 'B', 'x'. Index order:
 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22
 a0 d0 g0 b1 d1 f1 c2 e2 a3 b3 c3 e3 f3 g3 c4 d4 e4 b5 d5 f5 a6 d6 g6
"""

# ---------------------------------------------------------------- helpers

def read_board(path):
    with open(path) as f:
        board = f.read().strip()
    if len(board) != 23 or any(c not in "WBx" for c in board):
        raise ValueError(f"Invalid board in {path}: {board!r}")
    return board


def write_board(path, board):
    with open(path, "w") as f:
        f.write(board)


def swap_colors(board):
    return board.translate(str.maketrans("WB", "BW"))


def set_pieces(board, changes):
    """'b = copy of board; b[location] = piece' for each (location, piece)."""
    b = list(board)
    for location, piece in changes:
        b[location] = piece
    return "".join(b)

# ---------------------------------------------------------------- neighbors

NEIGHBORS = [
    [1, 3, 8],         # 0  a0
    [0, 2, 4],         # 1  d0
    [1, 5, 13],        # 2  g0
    [0, 4, 6, 9],      # 3  b1
    [1, 3, 5],         # 4  d1
    [2, 4, 7, 12],     # 5  f1
    [3, 7, 10],        # 6  c2
    [5, 6, 11],        # 7  e2
    [0, 9, 20],        # 8  a3
    [3, 8, 10, 17],    # 9  b3
    [6, 9, 14],        # 10 c3
    [7, 12, 16],       # 11 e3
    [5, 11, 13, 19],   # 12 f3
    [2, 12, 22],       # 13 g3
    [10, 15, 17],      # 14 c4
    [14, 16, 18],      # 15 d4
    [11, 15, 19],      # 16 e4
    [9, 14, 18, 20],   # 17 b5
    [15, 17, 19, 21],  # 18 d5
    [12, 16, 18, 22],  # 19 f5
    [8, 17, 21],       # 20 a6
    [18, 20, 22],      # 21 d6
    [13, 19, 21],      # 22 g6
]


def neighbors(j):
    return NEIGHBORS[j]

# ---------------------------------------------------------------- closeMill

MILLS = [
    # rows
    (0, 1, 2), (3, 4, 5), (8, 9, 10), (11, 12, 13),
    (14, 15, 16), (17, 18, 19), (20, 21, 22),
    # columns
    (0, 8, 20), (3, 9, 17), (6, 10, 14), (15, 18, 21),
    (7, 11, 16), (5, 12, 19), (2, 13, 22),
    # diagonals
    (0, 3, 6), (2, 5, 7), (20, 17, 14), (22, 19, 16),
]

# MILLS_AT[j] = pairs that complete a mill with j (switch cases)
MILLS_AT = [[] for _ in range(23)]
for _mill in MILLS:
    for _j in _mill:
        MILLS_AT[_j].append(tuple(k for k in _mill if k != _j))


def closeMill(j, b):
    C = b[j]
    assert C != 'x', "closeMill called on an empty location"
    return any(b[p] == C and b[q] == C for p, q in MILLS_AT[j])

# ---------------------------------------------------------------- move generators (White)

def GenerateRemove(b, L):
    added = False
    for location in range(23):
        if b[location] == 'B':
            if not closeMill(location, b):
                L.append(set_pieces(b, [(location, 'x')]))
                added = True
    if not added:          # all black pieces are in mills
        L.append(b)


def GenerateAdd(board):
    L = []
    for location in range(23):
        if board[location] == 'x':
            b = set_pieces(board, [(location, 'W')])
            if closeMill(location, b):
                GenerateRemove(b, L)
            else:
                L.append(b)
    return L


def GenerateMove(board):
    L = []
    for location in range(23):
        if board[location] == 'W':
            for j in neighbors(location):
                if board[j] == 'x':
                    b = set_pieces(board, [(location, 'x'), (j, 'W')])
                    if closeMill(j, b):
                        GenerateRemove(b, L)
                    else:
                        L.append(b)
    return L


def GenerateHopping(board):
    L = []
    for alpha in range(23):
        if board[alpha] == 'W':
            for beta in range(23):
                if board[beta] == 'x':
                    b = set_pieces(board, [(alpha, 'x'), (beta, 'W')])
                    if closeMill(beta, b):
                        GenerateRemove(b, L)
                    else:
                        L.append(b)
    return L


def GenerateMovesOpening(board):
    return GenerateAdd(board)


def GenerateMovesMidgameEndgame(board):
    if board.count('W') == 3:
        return GenerateHopping(board)
    else:
        return GenerateMove(board)

# ---------------------------------------------------------------- move generators (Black)

def GenerateMovesOpeningBlack(board):
    return [swap_colors(p) for p in GenerateMovesOpening(swap_colors(board))]


def GenerateMovesMidgameEndgameBlack(board):
    return [swap_colors(p) for p in GenerateMovesMidgameEndgame(swap_colors(board))]

# ---------------------------------------------------------------- static estimation

def staticEstimationOpening(board):
    numWhitePieces = board.count('W')
    numBlackPieces = board.count('B')
    return numWhitePieces - numBlackPieces


def staticEstimationMidgameEndgame(board):
    numWhitePieces = board.count('W')
    numBlackPieces = board.count('B')
    L = GenerateMovesMidgameEndgameBlack(board)
    numBlackMoves = len(L)
    if numBlackPieces <= 2:
        return 10000
    elif numWhitePieces <= 2:
        return -10000
    elif numBlackMoves == 0:
        return 10000
    else:
        return 1000 * (numWhitePieces - numBlackPieces) - numBlackMoves