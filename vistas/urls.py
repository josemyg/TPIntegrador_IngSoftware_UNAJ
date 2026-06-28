from django.urls import path
from . import views
from django.conf.urls import include
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import path, reverse_lazy


app_name = 'vistas'

urlpatterns = [
    path('', views.dashboard_cliente, name='dashboard_bienvenida'),
    path('perfil/editar/', views.ClientePerfilUpdateView.as_view(), name='cliente_perfil_update'),
    path('mis-actividades/', views.mis_actividades, name='mis_actividades'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('mis-reservas/crear/', views.mis_reservas_crear, name='mis_reservas_crear'),
    path('mis-reservas/cancelar/<int:reserva_id>/', views.mis_reservas_cancelar, name='mis_reservas_cancelar'),
    path('mis-reservas/descartar/<int:reserva_id>/', views.cancelar_pago_y_reserva, name='cancelar_pago_y_reserva'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('cambiar-contrasena/', PasswordChangeView.as_view(
    template_name='vistas/cambio_contrasena.html',
    success_url=reverse_lazy('vistas:cambio_contrasena_exitoso')
), name='cambio_contrasena'),
    path('cambiar-contrasena/exitoso/', PasswordChangeDoneView.as_view(template_name='vistas/cambio_contrasena_exitoso.html'), 
    name='cambio_contrasena_exitoso'),
]
