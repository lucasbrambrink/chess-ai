from django.conf.urls import url
from .views import GameView, InitGameView

urlpatterns = [
    url(r'^new/$', InitGameView.as_view(), name='new_game'),
    url(r'^live/(?P<game_id>[\w]+)', GameView.as_view(), name='live')
]
