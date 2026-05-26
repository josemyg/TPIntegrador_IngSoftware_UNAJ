from django.urls import path
from . import views

urlpatterns = [
    path('', views.gestion_reservas, name='lista_reservas'),
]