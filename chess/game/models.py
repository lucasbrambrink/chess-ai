from django.db import models
from hashlib import sha256
from datetime import datetime
from os import urandom
from django.contrib.postgres.fields import JSONField, ArrayField
import json
from .utils import *
from .api.v0.serializers import GameSerializer
from .conf import BLACK, WHITE


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
        self.chat = []

        for color in Piece.COLORS:
            for i, set_of_pieces in enumerate((self.FIRST_RANK,
                                               self.SECOND_RANK)):
                rank = i + 1 if color == WHITE else 8 - i
                self.initialize_rank(set_of_pieces, color, rank)

    def __iter__(self):
        yield ('game_id', self.id)
        yield ('last_color_played', self.last_color_played)
        yield ('moves', self.board.moves)
        yield ('chat', self.chat)

    def move(self, command, color):
        self.board.step(command, color)

    def add_chat(self, chat_line, color):
        color = 'White' if color == Piece.WHITE else 'Black'
        chat = '%s: %s' % (color, chat_line)
        Chat.objects.create(line=chat,
                            game_instance=GameInstance.objects.get(game_id=self.id))
        self.chat.append(chat)

    def print_moves(self):
        moves = (m for m in self.board.moves)
        for i, move in enumerate(moves):
            try:
                next_move = next(moves)[1]
            except StopIteration:
                next_move = None

            yield ('{}.'.format(i + 1), move[1], next_move or '')

    @property
    def serialized(self):
        as_dict = GameSerializer(self).data
        as_dict['player_keys'] = self.player_keys
        return as_dict

    @classmethod
    def initialize_from_dict(cls, game):
        new_game = cls()
        new_game.id = game.get('game_id')
        new_game.last_color_played = game.get('last_color_played')
        new_game.player_keys = game.get('player_keys')
        previous_board = game.get('board')
        for square in previous_board.get('squares', []):
            position = square.get('position')
            piece = square.get('piece')
            new_piece = None
            if piece is not None:
                new_piece = PieceFactory.create(piece.get('symbol'),
                                                position,
                                                piece.get('color'),
                                                piece.get('has_moved'))

            existing_square = new_game.board[position]
            existing_square.piece = new_piece

        new_game.board.moves = game.get('moves', [])
        new_game.chat = Chat.objects.filter(game_instance__game_id=new_game.id).values_list('line', flat=True)
        return new_game

    @classmethod
    def load_from_id(cls, game_id):
        game_instance = GameInstance.objects.get(game_id=game_id)
        return cls.initialize_from_dict(game_instance.__dict__)

    @property
    def next_color(self):
        next_ = BLACK if self.last_color_played == WHITE else WHITE
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

    def save(self):
        try:
            instance = GameInstance.objects.get(game_id=self.id)
        except GameInstance.DoesNotExist:
            instance = GameInstance.load_from(self.serialized)
        instance.board = self.serialized['board']
        instance.save()


class Chat(models.Model):
    line = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    game_instance = models.ForeignKey(to='GameInstance')


class GameInstance(models.Model):
    game_id = models.CharField(max_length=255)
    last_color_played = models.CharField(max_length=2)
    moves = JSONField
    player_keys = JSONField()
    board = JSONField()

    @classmethod
    def load_from(cls, game):
        if isinstance(game, Game):
            game = game.serialized
        else:
            assert type(game) is dict
        instance = cls(game_id=game['game_id'],
                       last_color_played=game['last_color_played'],
                       player_keys=game['player_keys'],
                       board=game['board'])
        return instance

