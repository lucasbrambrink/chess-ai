from django.shortcuts import render
from django.views.generic import TemplateView


class GameView(TemplateView):
    template_name = 'game/game.html'


