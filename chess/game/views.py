from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Game


class GameView(TemplateView):
    template_name = 'game/game.html'

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)
        game = Game()
        context['rows'] = game.board.as_descending_rows
        return context
