from django.db import models
from .utils import *
# Create your models here.




class Game(object):
    SECOND_RANK = tuple(
        Pawn for _ in range(8)
    )
    FIRST_RANK = (
        Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook
    )

    def __init__(self):
        self.board = Board()
        for color in Piece.COLORS:
            for i, set_of_pieces in enumerate((self.FIRST_RANK,
                                               self.SECOND_RANK)):
                rank = i + 1 if color == Piece.WHITE else 8 - i
                self.initialize_rank(set_of_pieces, color, rank)

    def initialize_rank(self, set_of_pieces, color, rank):
        for file_, piece in zip(Square.FILES, set_of_pieces):
            p = piece(position=Square(file_, rank), color=color)
            self.board[p.position] = p

    def __repr__(self):
        rows_as_strings = []
        for row in self.board.as_descending_rows:
            string = ''.join(['[ ]' if square.is_empty else '[{}]'.format(square.piece.symbol)
                     for square in row])
            string += '\n'
            rows_as_strings.append(string)
        return ''.join(rows_as_strings)

    def step(self, command, color):
        symbol, square = CommandParser.__call__(command)
        possible_pieces = [piece for piece in self.board.pieces
                           if (piece.color == color and
                               piece.symbol == symbol and
                               square in piece.available_steps(self.board))]
        if len(possible_pieces) != 1:
            print(possible_pieces)
            raise ValueError('That command is ambiguous')

        piece = possible_pieces[0]
        self.board[piece.position].piece = None
        piece.position = square
        self.board[piece.position] = piece
        print(self)



