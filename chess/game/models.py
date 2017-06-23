from django.db import models
from hashlib import sha256
from datetime import datetime
from os import urandom
from .utils import *


class Game(object):
    SECOND_RANK = tuple(
        Pawn for _ in range(8)
    )
    FIRST_RANK = (
        Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook
    )

    def assign_id(self):
        id = sha256(urandom(5)).hexdigest()[:10]
        return id

    def generate_player_keys(self):
        timestamp = str(datetime.now())
        salt = str(urandom(5))
        keys = {}
        for color in (Piece.COLORS):
            key_string = '%s%s%s' % (salt, timestamp, color)
            hash_ = sha256(key_string.encode()).hexdigest()
            keys[color] = hash_

        return keys

    def __init__(self):
        self.board = Board()
        self.id = self.assign_id()
        self.last_color_played = Piece.BLACK
        # initialize player keys
        self.player_keys = self.generate_player_keys()

        for color in Piece.COLORS:
            for i, set_of_pieces in enumerate((self.FIRST_RANK,
                                               self.SECOND_RANK)):
                rank = i + 1 if color == Piece.WHITE else 8 - i
                self.initialize_rank(set_of_pieces, color, rank)

    def __iter__(self):
        yield ('id', self.id)
        yield ('last_color_played', self.last_color_played)

    @property
    def next_color(self):
        next_ = Piece.BLACK if self.last_color_played == Piece.WHITE else Piece.WHITE
        self.last_color_played = next_
        return next_

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

    def king_is_in_check(self):
        for color in Piece.COLORS:
            king = self.board.get_king(color)
            if king.is_in_check(self.board):
                return (True, king)

        return (False, None)


class GameInstance(models.Model):
    game_id = models.CharField(max_length=255)
    last_color_played = models.CharField(max_length=2)
    white_player_key = models.CharField(max_length=255)
    black_player_key = models.CharField(max_length=255)
    board = models.TextField()
