# from snippets.models import Snippet
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from django.core.cache import cache
from django.shortcuts import redirect


class GameApiView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        game_id = kwargs.get('game_id')
        game = cache.get(game_id)
        if game is None:
            return redirect('new_game')

        squares = []
        for row in game.board.as_descending_rows:
            for square in row:
                square_dict = dict(square)

                if square.piece is not None:
                    piece = dict(square.piece)
                    piece['available_moves'] = list(str(move) for move in
                                                    square.piece.available_steps(game.board))
                    square_dict['piece'] = piece

                squares.append(square_dict)

        board = {'squares': squares}
        game_as_dict = dict(game)
        game_as_dict['board'] = board
        return Response(game_as_dict, status=status.HTTP_200_OK)

