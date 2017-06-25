from rest_framework import serializers

import logging

log = logging.getLogger(__name__)


class PieceSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=1)
    position = serializers.CharField(max_length=2)
    color = serializers.CharField(max_length=1)
    available_moves = serializers.ListField(child=serializers.CharField(max_length=6))


class SquareSerializer(serializers.Serializer):
    position = serializers.CharField(max_length=2)
    piece = PieceSerializer(read_only=True,
                            allow_null=True)


class BoardSerializer(serializers.Serializer):
    squares = SquareSerializer(many=True,
                               read_only=True,
                               allow_null=True)


# class GameSerializer(serializers.Serializer):
#     id = serializers.CharField(max_length=255)
#     last_color_played = serializers.CharField(max_length=1)
#     board = BoardSerializer(read_only=True)



class GameSerializer(object):

    def __init__(self, game):
        self.data = self.serialize(game)

    @classmethod
    def serialize(cls, game):
        squares = []
        for row in game.board.as_descending_rows:
            for square in row:
                square_dict = dict(square)

                if square.piece is not None:
                    piece = dict(square.piece)

                    piece['available_moves'] = list(square.as_consumable_move(move, square.piece) for move in
                                                    square.piece.available_steps(game.board,
                                                                                 translate=True))
                    square_dict['piece'] = piece

                squares.append(square_dict)

        board = {'squares': squares}
        game_as_dict = dict(game)
        game_as_dict['board'] = board
        return game_as_dict