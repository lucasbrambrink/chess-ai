from rest_framework import serializers
from ...models import Game

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


class GameSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    last_color_played = serializers.CharField(max_length=1)
    board = BoardSerializer(read_only=True)