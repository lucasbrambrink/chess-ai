
from django.shortcuts import render, reverse
from django.views.generic import TemplateView, RedirectView
from .models import Game
from .forms import CommandForm
from django.core.cache import cache


class InitGameView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        game = Game()
        cache.set(game.id, game)
        return reverse('live', args=(game.id,))


class GameView(TemplateView):
    template_name = 'game/game.html'

    def get_context_data(self, **kwargs):
        game_id = kwargs.get('game_id')
        game = cache.get(game_id)
        if game is None:
            raise ValueError('The game is not in cache!')

        context = super(GameView, self).get_context_data(**kwargs)
        context['rows'] = game.board.as_descending_rows
        context['command_form'] = CommandForm()
        return context

    def post(self, request, game_id, **kwargs):
        game = cache.get(game_id)
        if game is None:
            raise ValueError('The game is not in cache!')

        form = CommandForm(request.POST)
        if form.is_valid():
            game.step(form.cleaned_data['command'], game.next_color)

        context = super(GameView, self).get_context_data(**kwargs)
        context['rows'] = game.board.as_descending_rows
        context['command_form'] = CommandForm()
        cache.set(game.id, game)
        return render(request, self.template_name, context)
