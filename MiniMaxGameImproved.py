"""Improved implementation of MiniMaxGame.py, computes white's maxima move in the fixed midgame/endgame phase."""

import sys
from cli_helper import (
            _search, 
            _run_cli
)
from morris import (
            GenerateMovesMidgameEndgame,
            GenerateMovesMidgameEndgameBlack,
            MILLS,
            neighbors
)

def ImprovedSEFGame_1(board):
        '''Balanced play style which attempts to take into account different board properties like player mobility, potential mill difference, and material difference'''
        numWhitePieces = board.count('W')
        numBlackPieces = board.count('B')
    
        # Terminal state checks (same as baseline)
        if numBlackPieces <= 2:
            return 10000
        elif numWhitePieces <= 2:
            return -10000
    
        whiteMoves = GenerateMovesMidgameEndgame(board)
        blackMoves = GenerateMovesMidgameEndgameBlack(board)
    
        if len(blackMoves) == 0:
            return 10000
        if len(whiteMoves) == 0:
            return -10000

        # Count potential mill setups
        white2Pieces = 0
        black2Pieces = 0
        for mill in MILLS:
            pieces = [board[i] for i in mill]
        if pieces.count('W') == 2 and pieces.count('x') == 1:
            white2Pieces += 1
        elif pieces.count('B') == 2 and pieces.count('x') == 1:
            black2Pieces += 1

        # Weighted evaluation:
        # 1000 * Material Difference + 10 * Mobility Difference + 20 * Potential Mill Difference
        pieceScore = 1000 * (numWhitePieces - numBlackPieces)
        mobilityScore = 10 * (len(whiteMoves) - len(blackMoves))
        millSetupScore = 20 * (white2Pieces - black2Pieces)

        return pieceScore + mobilityScore + millSetupScore

def ImprovedSEFGame_2(board):
    '''SEF that prioritieses reducing the mobility of the opposing player while maximizing that of the active player'''
    numWhitePieces = board.count('W')
    numBlackPieces = board.count('B')
    
    if numBlackPieces <= 2:
        return 10000
    if numWhitePieces <= 2:
        return -10000
        
    whiteMoves = len(GenerateMovesMidgameEndgame(board))
    blackMoves = len(GenerateMovesMidgameEndgameBlack(board))
    
    if blackMoves == 0:
        return 10000
    if whiteMoves == 0:
        return -10000
        
    # Heavily weights move restrictions (Mobility Delta)
    # Penalizes situations where Black has high mobility options
    pieceScore = 1000 * (numWhitePieces - numBlackPieces)
    mobilityScore = 50 * whiteMoves - 80 * blackMoves
    
    return pieceScore + mobilityScore

def ImprovedSEFGame_3(board):
    '''Heuristic which attempts to setup safe mill cycles i.e. mills which it can safely move 1 piece and then move it back to recreate a mill'''
    numWhitePieces = board.count('W')
    numBlackPieces = board.count('B')
    
    if numBlackPieces <= 2:
        return 10000
    if numWhitePieces <= 2:
        return -10000

    # Count formed mills that have an adjacent empty spot to open and close
    whiteActiveMillCycles = 0
    blackActiveMillCycles = 0
    
    for mill in MILLS:
        pieces = [board[i] for i in mill]
        if pieces.count('W') == 3:
            # Check if any piece in the mill has an empty neighbor to slide out to
            if any(any(board[n] == 'x' for n in neighbors(idx)) for idx in mill):
                whiteActiveMillCycles += 1
        elif pieces.count('B') == 3:
            if any(any(board[n] == 'x' for n in neighbors(idx)) for idx in mill):
                blackActiveMillCycles += 1

    pieceScore = 1000 * (numWhitePieces - numBlackPieces)
    cycleScore = 150 * (whiteActiveMillCycles - blackActiveMillCycles)
    
    return pieceScore + cycleScore


def MiniMaxGameImproved(board, depth, evaluation=ImprovedSEFGame_1):
        return _search(
                    board, 
                    depth,
                    GenerateMovesMidgameEndgame,
                    GenerateMovesMidgameEndgame,
                    evaluation
                )

if __name__ == "__main__":
    sys.exit(_run_cli(MiniMaxGameImproved))
