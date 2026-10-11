import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))


from morris import(
        swap_colors,
        GenerateMovesOpening,
        GenerateMovesOpeningBlack,
        GenerateMovesMidgameEndgame,
        GenerateMovesMidgameEndgameBlack
)
from cli_helper import(
        _search
)
from MiniMaxOpeningImproved import(
        ImprovedSEFOpening_1,
        ImprovedSEFOpening_2,
        ImprovedSEFOpening_3,
        MiniMaxOpeningImproved
)
from MiniMaxGameImproved import(
        ImprovedSEFGame_1,
        ImprovedSEFGame_2,
        ImprovedSEFGame_3,
        MiniMaxGameImproved
)

class Player():

    def __init__(self, op, mid, player_color):
        self.turn = 0
        self.opening_sef = op
        self.midgame_sef = mid
        self.player_color = player_color
    
    def __repr__(self):
        return f"Player(Color: {self.player_color}, Opening SEF: {self.opening_sef}, MidGame SEF: {self.midgame_sef})"

    def ResetTurns(self):
        self.turn = 0

    def PlayTurn(self, board, depth):
        if self.turn < 9:
            evaluation = self.opening_sef
            white_gen = GenerateMovesOpening
            black_gen = GenerateMovesOpeningBlack
        else:
            evaluation = self.midgame_sef
            white_gen = GenerateMovesMidgameEndgame
            black_gen = GenerateMovesMidgameEndgameBlack

        if self.player_color == "B":
            board = swap_colors(board)

        estimate, best_board, positions_evaluated = _search(
            board,
            depth,
            white_gen,
            black_gen,
            evaluation=evaluation,
            pruning=True
            )

        if self.player_color == "B":
            best_board = swap_colors(best_board)

        self.turn += 1
        return best_board

def IsGameOver(board, turns):

    if turns < 10:
        return False

    num_white = board.count('W')
    num_black = board.count('B')
    
    if num_white < 3:
        return True
    if num_black < 3:
        return True
        
    if num_white + num_black > 6:  
        if len(GenerateMovesMidgameEndgame(board)) == 0:
            return True
        if len(GenerateMovesMidgameEndgameBlack(board)) == 0:
            return True
            
    return None 

def WhoWon(board, turns):

    if turns < 10:
        return

    num_white = board.count('W')
    num_black = board.count('B')

    if num_white < 3:
        return "B"
    if num_black < 3:
        return "W"
        
    if num_white + num_black > 6:  
        if len(GenerateMovesMidgameEndgame(board)) == 0:
            return "B"
        if len(GenerateMovesMidgameEndgameBlack(board)) == 0:
            return "W"

def PlayMatch(w_player, b_player):
    board = "xxxxxxxxxxxxxxxxxxxxxxx" 
    turns = 0
    winning_color = None
    winning_implementaion = None
    losing_implementation = None

    is_game_over = False

    while(not is_game_over):
        board = w_player.PlayTurn(board, 5)
        print(f"\t({turns}) White Player: {board}")
        is_game_over = IsGameOver(board, turns)
        if (is_game_over):
            break

        board = b_player.PlayTurn(board, 5)
        print(f"\t({turns + 1}) Black Player: {board}")
        is_game_over = IsGameOver(board, turns)
        if (is_game_over):
            break

        turns += 1

        if turns >= 30:
            break

    winning_color = WhoWon(board, turns + 1)

    if winning_color == "W":
        winning_implementation = w_player
        losing_implementation = b_player
    elif winning_color == "B":
        winning_implementation = b_player
        losing_implementation = w_player
    else:
        winning_implementation = None
        Losing_implementation = None

    w_player.ResetTurns()
    b_player.ResetTurns()

    return [turns, winning_color, winning_implementation, losing_implementation, board]

def TestModels():
    # Define your configuration tuples or classes instead of static instances
    # sef_w_configs = [ImprovedSEFOpening_1, ImprovedSEFOpening_2, ImprovedSEFOpening_3]
    # sef_b_configs = [ImprovedSEFOpening_1, ImprovedSEFOpening_2, ImprovedSEFOpening_3]

    print("Results:")
    for op_w in [ImprovedSEFOpening_1, ImprovedSEFOpening_2, ImprovedSEFOpening_3]: 
        for mid_w in [ImprovedSEFGame_1, ImprovedSEFGame_2, ImprovedSEFGame_3]:
            for op_b in [ImprovedSEFOpening_1, ImprovedSEFOpening_2, ImprovedSEFOpening_3]:
                for mid_b in [ImprovedSEFGame_1, ImprovedSEFGame_2, ImprovedSEFGame_3]:
                    
                    w_player = Player(op_w, mid_w, "W")
                    b_player = Player(op_b, mid_b, "B")
                    
                    match_result = PlayMatch(w_player, b_player) 
                    print(f"Match Results: \n (Turns) {match_result[0]}, \n (Winning Color) {match_result[1]} \n (Winning Implementation) {repr(match_result[2])} \n (Losing Implementation) {repr(match_result[3])} \n (Final Board) {match_result[4]}")

if __name__ == "__main__":
    sys.exit(TestModels())
