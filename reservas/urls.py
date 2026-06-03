from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.gestion_reservas,
        name='lista_reservas'
    ),

    path(
        'editar/<int:id>/', 
        views.editar_reserva,
        name='editar_reserva'
    ),

    path(
        'cancelar/<int:id>/',
        views.cancelar_reserva,
        name='cancelar_reserva'
    ),

] # Define las rutas URL para la aplicación de reservas. Cada ruta está asociada a una vista específica que maneja la lógica correspondiente para listar, editar o cancelar reservas.