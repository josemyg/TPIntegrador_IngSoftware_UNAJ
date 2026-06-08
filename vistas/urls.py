from django.urls import path
from . import views
from django.conf.urls import include


app_name = 'vistas'

urlpatterns = [
    path('bienvenido', views.dashboard_cliente, name='dashboard_bienvenida'),
    path('perfil/editar/', views.ClientePerfilUpdateView.as_view(), name='cliente_perfil_update'),
    path('mis-actividades/', views.mis_actividades, name='mis_actividades'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('mis-reservas/crear/', views.mis_reservas_crear, name='mis_reservas_crear'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
]
