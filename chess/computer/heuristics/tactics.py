from copy import deepcopy
from .base import Heuristic


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


