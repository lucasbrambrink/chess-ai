from copy import deepcopy
from .base import Heuristic


class MinMaxInspection(Heuristic):
    """
    1 unit of inspection
        for each move:
            -> hypothetical_board
            -> find MAX move for opponent


        -> find MIN of (MAX moves)

    - allow to apply recursively
    """

    def evaluate_board(self, board, playing_as):
        white, black = board.score

        pass


    def apply(self, board, playing_as):
        opponent_color = board.opponent_color(playing_as)
        initial_score = board.score
        best_sequence = (None, None)
        for piece in board.player_pieces(playing_as):
            for move in piece.available_steps(board):
                hypothetical_board = deepcopy(board)
                hypothetical_board.step(move, playing_as)
                # now inspect the available moves of the opponent
                for opponent_piece in hypothetical_board.player_pieces(opponent_color):
                    for opponent_move in opponent_piece.available_steps(hypothetical_board):
                        inspection_board = deepcopy(hypothetical_board)
                        inspection_board.step(opponent_move, opponent_color)
                        # quantify strength of move
                        current_score = inspection_board.score
                        difference = 0



class Tactics(Heuristic):
    name = 'tactics'

    def apply(self, board, playing_as):
        """
        inspect moves into hypothetical positions

        1st level
        ##

            - every possible move, if made, would
                A) loose material / gain material?
                B) leave piece attacked, undefended?
                C) identify if piece is defended




        :param board:
        :return:
        """
        pass


