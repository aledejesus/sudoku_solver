from django.conf.urls import url
from . import views as home_views

urlpatterns = [
    url(r'^', home_views.home),
]
