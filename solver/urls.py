from django.conf.urls import url
from . import views as solver_views

urlpatterns = [
    url(r'^$', solver_views.choose_method),
    url(r'numbers/', solver_views.input_numbers),
    url(r'test_solver/', solver_views.test_solver),
]
