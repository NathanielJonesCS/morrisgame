# CS4346 Morris Game AI 

## Overview

**Files**
- MiniMaxOpening.py: Computes whites best move during the oppening phase of the game
- MiniMaxGame.py: Computes whites best move during the mid/end-game phase
- ABOpening.py & ABGame.py: Reimplements the previous 2 files, this time making use of ALPHA-BETA prunging to shorten runtimes.
- MiniMaxOpeningBlack.py & MiniMaxGameBlack.py: Reimplementations of first 2 files, this time computing blacks best move during opening/mid/end-game phases of play
- MiniMaxOpeningImpoved.py & MiniMaxGameImproved.py: Upgrades on the supplied static estimation function located in `morris.py`.

## Evaluating Static Estimation Functions
For this project we were given a set of static estimation functions (SEFs) which can be seen below.
```
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

```

As the implementations above are quite basic we have gone ahead and implemented a series of improved SEFs. These SEFs have been tested thorhough a 2 step process, first we ran them on the test boards located within the `./boards` directory. These test boards have been designed to display an implementations ability (or lack thereof) to take advantage of things like potential mills, block enemy mills, populate important locations on the board, etc. Boards found in `./boards` have been specifically designed to test each implementations ability to perform during both the opening game (boards 0-4) and mid/endgame (boards 5-9). 

The second step was to how they performed in real matches, to mimic real matches we made the different AI's play a match against each other. The determination of the best SEF is covered in `MyStaticEstimation.txt` file, to run the tests yourself run the `tournament.py` script in the `/tests` directory.

*Note: All SEF implementation can be found at `MiniMaxOpeningImporved.py` & `MiniMaxGameImproved.py`, those which are being used by the `MinimaxOpeingImproved` and `MiniMaxgameImproved` are the ones we have found to perform the best.*

**Tournament.py**
Tournament.py is a script utilized to make the different imporved SEF implementations be used agains each other. This script was run using various different depths to see how each stratagy faired at different depths. To see the output files produced by running tournament.py take a look at the `/tournament_results/` directory.

At a depth of 3 (with an 81 game tournament) 31 games led to a white victory (38.3%), 17 to a black victory (21.0%), and 33 to a draw (40.7%), a draw here being defined as any game that goes over 100 turns without a winner. The SEF that lead to the most wins (19 out of 31) was ImprovedGameSEF_1 while the opening strategies were mixed and no clear front-runner could be determined. Interestingly, of the 33 matches that ended in a draw 17 endeded in a looping pattern while only 16 showed no clear looping pattern, an indication that these games may have lead to a winner if they had gone on for more than 100 turns. Another thing to make note of is the variance with most games that ended in a Win/Lose being quite short at only about 16-22 turns with the longest of these Win/Lose games being only 30 turns long.

At a depth of 5 (with an 81 game tournament) 22 games led to a white victory (27.2%), 4 to a black victory (4.9%), and 55 to a draw (67.9%). Note that here we lowered the criterion for a draw from 100 turns to just 30 turns, this is done both to save processing time and as it was noted that longer games tend to be those in which AI players had gotten stuck in repetitive turn loop. Here we found that `ImprovedSEFOpening_3` and `ImprovedSEFOpening_1` were essentially tied (13 and 11 wins) while `ImprovedSEFGame_1` (13 wins) came out as the front runner in the game SEF's. It was believed that the restriction to just 30 turns lead to the increase in the draw count but on closer insepction (testing a few of the SEF implementations that lead to a draw at 30 turns) we found that they would mostly just get stuck in the "Flying" phase of play. 


## Testing
Test scripts have also been implemented to help correct potential issues in development. These include things like unittestingand benchmarking. These scripts can be found within the `./tests` directory.
