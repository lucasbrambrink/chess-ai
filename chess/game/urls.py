from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^api/', include('game.api.v0.urls')),
    url(r'^new/$', views.NewGameRedirect.as_view(), name='new_game'),
    url(r'^live/(?P<game_id>[\w]+)/$', views.InitGameView.as_view(), name='pick_color'),
    url(r'^live/(?P<game_id>[\w]+)/(?P<color>[b|w])$', views.GameView.as_view(), name='live'),
    url(r'^live/(?P<game_id>[\w]+)/(?P<color>[b|w])/submit_move$', views.SubmitMoveView.as_view(), name='live_post'),
    url(r'^live/(?P<game_id>[\w]+)/(?P<color>[b|w])/(?P<last_color>[b|w])', views.DiffView.as_view(), name='diff'),
]
