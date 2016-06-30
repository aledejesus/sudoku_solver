from django.conf.urls import url
from . import views as solver_views

urlpatterns = [
    url(r'^', solver_views.choose_method),
]
