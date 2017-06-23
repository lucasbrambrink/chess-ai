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

        return Response(serializers.GameSerializer(game).data,
                        status=status.HTTP_200_OK)

