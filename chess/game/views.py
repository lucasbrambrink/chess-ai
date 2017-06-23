import random
from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView, RedirectView, View
from django.http.response import HttpResponseRedirect, HttpResponseNotAllowed
from .models import Game, Piece
from .forms import CommandForm, InitGameForm
from django.core.cache import cache
from django.http import JsonResponse


PLAYER_KEY = 'player_key'


class NewGameRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        game = Game()
        cache.set(game.id, game)
        return reverse('pick_color', args=(game.id,))


class InitGameView(TemplateView):
    template_name = 'game/init.html'

    def get_context_data(self, **kwargs):
        return {
            'init_form': InitGameForm()
        }

    def post(self, request, game_id):
        form = InitGameForm(request.POST)
        if not form.is_valid():
            raise ValueError()

        color = form.data.get('color')
        game = cache.get(game_id)
        if game is None:
            raise ValueError()

        request.session[PLAYER_KEY] = game.player_keys[color]
        return HttpResponseRedirect(reverse('live', args=(game_id, color)))


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
        color = kwargs.get('color')
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
        context['submit_url'] = reverse('live_post', args=(game.id, color))
        return context


class SubmitMoveView(View):

    def post(self, request, game_id, color, **kwargs):
        game = cache.get(game_id)
        if game is None:
            raise ValueError('The game is not in cache!')

        redirect_response = redirect(reverse('live', args=(game.id, color)))
        if game.last_color_played == color:
            return redirect_response

        form = CommandForm(request.POST)
        if form.is_valid():
            try:
                player_key = request.session[PLAYER_KEY]
                if player_key != game.player_keys[color]:
                    return HttpResponseNotAllowed('You should not do that.')
                # import ipdb; ipdb.set_trace()
                game.step(form.cleaned_data['command'], game.next_color)
            except KeyError:
                return HttpResponseNotAllowed('You should not do that.')
            except ValueError:
                _ = game.next_color
                pass
            cache.set(game.id, game)

        return redirect_response


class DiffView(View):

    def get(self, request, game_id, color, last_color):
        game = cache.get(game_id)
        if game is None:
            raise ValueError('The game is not in cache!')

        changed = game.last_color_played.lower() != last_color
        return JsonResponse({'changed': changed})
