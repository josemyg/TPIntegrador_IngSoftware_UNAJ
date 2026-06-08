from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import *



urlpatterns = [
    path('', RegistroClienteCreateView.as_view(), name = 'registro_cliente'),
]   