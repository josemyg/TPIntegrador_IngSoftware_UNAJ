from django.urls import path
from . import views

urlpatterns = [
    path(
        'crear/',
        views.crear_reserva,
        name='crear_reserva'
    ),
    # La ruta raíz de la aplicación de reservas, que se asocia con la vista gestion_reservas.
    path(
        '', 
        views.gestion_reservas,
        name='lista_reservas'
    ),
    # La ruta para editar una reserva específica, que incluye un parámetro de ID para identificar la reserva a editar.
    path(
        'editar/<int:id>/', 
        views.editar_reserva,
        name='editar_reserva'
    ),
    # La ruta para cancelar una reserva específica, que también incluye un parámetro de ID para identificar la reserva a cancelar.
    path(
        'cancelar/<int:id>/',
        views.cancelar_reserva,
        name='cancelar_reserva'
    ),
    # La ruta para consultar la disponibilidad de canchas.
    path(
        'disponibilidad/',
        views.consultar_disponibilidad,
        name='consultar_disponibilidad'
    ),
    path(
        'reservas/rapida/', 
         views.generar_reserva_rapida, 
         name='generar_reserva_rapida'
         ),

]