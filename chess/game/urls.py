from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^api/', include('game.api.v0.urls')),
    url(r'^new/$', views.InitGameView.as_view(), name='new_game'),
    url(r'^live/(?P<game_id>[\w]+)$', views.GameView.as_view(), name='live'),
    url(r'^live/(?P<game_id>[\w]+)/submit_move$', views.SubmitMoveView.as_view(), name='live_post'),
    url(r'^live/(?P<game_id>[\w]+)/(?P<color>[b|w])', views.DiffView.as_view(), name='diff'),
]
