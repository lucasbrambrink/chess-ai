from django.conf.urls import url
from .views import GameView

urlpatterns = [
    url(r'^live/(?P<game_id>[0-9]+)', GameView.as_view(), name='live')
]
