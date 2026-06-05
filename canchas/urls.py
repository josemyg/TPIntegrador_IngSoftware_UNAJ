from django.urls import path
from . import views
from .views import (
    TipoCanchaListView, 
    TipoCanchaCreateView, 
    TipoCanchaUpdateView, 
    TipoCanchaDeleteView
)

urlpatterns = [
    path('tipos/', TipoCanchaListView.as_view(), name='tipo_cancha_list'),
    path('tipos/nuevo/', TipoCanchaCreateView.as_view(), name='tipo_cancha_create'),
    path('tipos/<int:pk>/editar/', TipoCanchaUpdateView.as_view(), name='tipo_cancha_update'),
    path('tipos/<int:pk>/eliminar/', TipoCanchaDeleteView.as_view(), name='tipo_cancha_delete'),
    path('tipos/<int:pk>/alternar-estado/', views.alternar_estado_cancha, name='tipo_cancha_toggle'),
    path('canchas/', views.CanchaListView.as_view(), name='cancha_list'),
    path('canchas/nuevo/', views.CanchaCreateView.as_view(), name='cancha_create'),
    path('canchas/<int:pk>/editar/', views.CanchaUpdateView.as_view(), name='cancha_update'),
    path('canchas/<int:pk>/eliminar/', views.CanchaDeleteView.as_view(), name='cancha_delete'),
    path('canchas/bloquear/<int:cancha_id>/', views.bloquear_cancha_view, name='cancha_bloquear'),
    path('canchas/activar/<int:cancha_id>/', views.activar_cancha_view, name='cancha_activar'),
]