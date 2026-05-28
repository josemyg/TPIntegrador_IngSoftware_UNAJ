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
]