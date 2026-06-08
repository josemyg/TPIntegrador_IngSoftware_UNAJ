from django.urls import path
from . import views

app_name = 'vistas'

urlpatterns = [
    path('bienvenido', views.dashboard_cliente, name='dashboard_bienvenida'),
    path('perfil/editar/', views.ClientePerfilUpdateView.as_view(), name='cliente_perfil_update'),
]


