from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^v0/live/(?P<game_id>[\w]+)$', views.GameApiView.as_view(), name='live'),
]
