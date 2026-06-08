from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import *

urlpatterns = [
    path('', RegistroClienteCreateView.as_view(), name = 'registro_cliente'),
    path('gracias', views.registro_exitoso_cliente, name = 'registro_cliente_exitoso'),
    path('blanqueo', ContrasenaClienteResetView.as_view(), name = 'inicio_contrasena_cliente'),
]   