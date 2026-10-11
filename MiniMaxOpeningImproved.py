"""Imporved implementation of MiniMaxOpening.py, computes white's maxima move in the fixed opening phase of a game."""

import sys
from cli_helper import(
        _search, 
        _run_cli
)
from morris import (
        GenerateMovesOpening, 
        GenerateMovesOpeningBlack,
        MILLS
)

# Improved Opening SEFs
def ImprovedSEFOpening_1(board):
    '''Priorities mill creation while taking into account the opponent players mill creation potential'''
    numWhitePieces = board.count('W')
    numBlackPieces = board.count('B')
    
    # Count potential mills (2 pieces of same color + 1 empty spot)
    whiteCloseMills = 0
    blackCloseMills = 0
    
    for mill in MILLS:
        pieces = [board[i] for i in mill]
        if pieces.count('W') == 2 and pieces.count('x') == 1:
            whiteCloseMills += 1
        elif pieces.count('B') == 2 and pieces.count('x') == 1:
            blackCloseMills += 1
            
    # Evaluation = Piece Advantage + Threatened Mill Advantage
    return (numWhitePieces - numBlackPieces) + 2 * (whiteCloseMills - blackCloseMills)

def ImprovedSEFOpening_2(board):
    '''Plays a strategy that prioritizes occupying important locations early on'''
    NODE_WEIGHTS = [
        3, 3, 3, 4, 3, 4, 3, 3, 3, 4, 3, 3, 4, 3, 3, 3, 3, 4, 4, 4, 3, 3, 3
    ]

    numWhitePieces = board.count('W')
    numBlackPieces = board.count('B')
    
    whitePosScore = sum(NODE_WEIGHTS[i] for i, piece in enumerate(board) if piece == 'W')
    blackPosScore = sum(NODE_WEIGHTS[i] for i, piece in enumerate(board) if piece == 'B')
    
    # Material difference (100x) + Positional control score
    return 100 * (numWhitePieces - numBlackPieces) + (whitePosScore - blackPosScore)

def ImprovedSEFOpening_3(board):
    '''Focuses on deying the enemy player the ability to develop 2 in a row mills i.e. aggressive blocking strategy'''
    numWhitePieces = board.count('W')
    numBlackPieces = board.count('B')
    
    whiteCloseMills = 0
    blackCloseMills = 0
    
    for mill in MILLS:
        pieces = [board[i] for i in mill]
        if pieces.count('W') == 2 and pieces.count('x') == 1:
            whiteCloseMills += 1
        elif pieces.count('B') == 2 and pieces.count('x') == 1:
            blackCloseMills += 1
            
    return (numWhitePieces - numBlackPieces) + (2 * whiteCloseMills) - (5 * blackCloseMills)


# 


def MiniMaxOpeningImproved(board, depth, evaluation=ImprovedSEFOpening_1):
    return _search(
                board, 
                depth,
                GenerateMovesOpening,
                GenerateMovesOpeningBlack,
                evaluation
            )

if __name__ == "__main__":
    sys.exit(_run_cli(MinimaxOpeningImproved))
