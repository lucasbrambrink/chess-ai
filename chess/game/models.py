from django.db import models
from .utils import *
# Create your models here.


class Game(object):

    def __init__(self):
        self.board = Board()
        self.square = Square('a', 1)
        self.pawn = Pawn(self.square, Piece.WHITE)
        self.bishop = Bishop(Square('c', 2), Piece.WHITE)
        self.rook = Rook(Square('g', 8), Piece.WHITE)
        self.queen = Queen(Square('e', 4), Piece.WHITE)

