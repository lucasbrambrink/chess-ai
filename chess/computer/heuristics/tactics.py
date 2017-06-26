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




class Tactics(Heuristic):
    name = 'tactics'

    def apply(self, board):
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


