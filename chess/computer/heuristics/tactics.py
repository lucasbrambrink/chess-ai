import logging
from copy import deepcopy
from .base import Heuristic

from game.conf import WHITE, BLACK


log = logging.getLogger(__name__)


class MinMaxInspection(Heuristic):
    """
    1 unit of inspection
        for each move:
            -> hypothetical_board
            -> find MAX move for opponent


        -> find MIN of (MAX moves)

    - allow to apply recursively
    """
    @staticmethod
    def score_difference(initial_score, score, playing_as):
        account_for_color = 1 if playing_as == WHITE else -1
        initial_standing = (initial_score[0] - initial_score[1]) * account_for_color
        current_standing = (score[0] - score[1]) * account_for_color
        return current_standing - initial_standing

    def best_opponent_move(self, opponent_moves, initial_score, playing_as):
        """
        take the min here because that is the opponents best score... e.g. -10
        """
        return min(opponent_moves,
                   key=lambda m: self.score_difference(
                       initial_score, m[0], playing_as))

    def apply(self, board, playing_as):
        opponent_color = board.opponent_color(playing_as)
        initial_score = board.score
        scored_moves = []
        piece_positions = set(p.position for p in board.player_pieces(playing_as))
        for position in piece_positions:
            piece = board[position].piece
            # import ipdb; ipdb.set_trace()
            for move in piece.available_steps(board):
                piece = board[position].piece
                if move not in piece.available_steps(board):
                    continue
                try:
                    board.step(piece.get_unambiguous_step(board, move), playing_as)
                except ValueError:
                    import ipdb; ipdb.set_trace()

                opponent_moves = []
                # now inspect the available moves of the opponent
                opponent_piece_positions = set(p.position for p in board.player_pieces(opponent_color))
                for position in opponent_piece_positions:
                    opponent_piece = board[position].piece
                    available_steps_for_opponent = opponent_piece.available_steps(board)
                    for opponent_move in available_steps_for_opponent:
                        opponent_piece = board[position].piece
                        # import ipdb; ipdb.set_trace()
                        try:
                            board.step(opponent_piece.get_unambiguous_step(board, opponent_move), opponent_color)
                        except ValueError:
                            # might still be in check, invalid move, ignore
                            log.info('{}: {}'.format(opponent_piece, opponent_move))
                            continue

                        # quantify strength of move
                        opponent_moves.append(
                            (board.score, opponent_move, opponent_piece)
                        )
                        board.revert_last_move()

                worst_score, best_opponent_move, opponent_piece = self.best_opponent_move(opponent_moves, initial_score, playing_as)
                scored_moves.append(
                    (worst_score, move, best_opponent_move, opponent_piece)
                )
                board.revert_last_move()

        return max(scored_moves,
                   key=lambda x: x[0])


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


