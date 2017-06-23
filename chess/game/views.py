import random
from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView, RedirectView, View
from .models import Game, Piece
from .forms import CommandForm
from django.core.cache import cache
from django.http import JsonResponse


PLAYER_KEY = 'player_key'


class InitGameView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        game = Game()
        playing_as = random.choice(Piece.COLORS)
        # self.request.session[PLAYER_KEY] = game.keys.get(playing_as)
        cache.set(game.id, game)
        return reverse('live', args=(game.id,))


class GameView(TemplateView):
    template_name = 'game/game.html'

    def dispatch(self, request, *args, **kwargs):
        game_id = kwargs.get('game_id')
        game = cache.get(game_id)
        if game is None:
            return redirect('new_game')

        return super(GameView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        game_id = kwargs.get('game_id')
        game = cache.get(game_id)
        if game is None:
            raise ValueError('The game is not in cache!')

        context = super(GameView, self).get_context_data(**kwargs)
        context['rows'] = game.board.as_descending_rows
        form = CommandForm()
        form.set_label(game.last_color_played)
        context['command_form'] = form
        context['color'] = game.last_color_played
        context['game_id'] = game.id
        is_in_check, piece = game.king_is_in_check()
        context['is_in_check'] = piece
        context['submit_url'] = reverse('live_post', args=(game.id,))
        return context


class SubmitMoveView(View):

    def post(self, request, game_id, **kwargs):
        game = cache.get(game_id)
        if game is None:
            raise ValueError('The game is not in cache!')

        form = CommandForm(request.POST)
        if form.is_valid():
            try:
                # player_key = request.session[PLAYER_KEY]
                import ipdb; ipdb.set_trace()
                # game.step(form.cleaned_data['command'], game.next_color)
            except KeyError:
                print('Unauthenticated player')
                pass
            except ValueError:
                _ = game.next_color
                pass
            cache.set(game.id, game)

        return redirect(reverse('live', args=(game.id,)))


class DiffView(View):

    def get(self, request, game_id, color):
        game = cache.get(game_id)
        if game is None:
            raise ValueError('The game is not in cache!')

        changed = game.last_color_played.lower() != color
        return JsonResponse({'changed': changed})
