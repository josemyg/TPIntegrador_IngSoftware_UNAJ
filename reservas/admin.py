from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_cancha', 'fecha', 'hora_inicio', 'estado', 'precio_final') # campos que se mostrarán en la lista de reservas en el panel de administración
    list_filter = ('fecha', 'estado', 'tipo_cancha')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__dni') 
    autocomplete_fields = ['cliente'] # Permite buscar clientes por nombre, apellido o DNI en el panel de administración al crear o editar una reserva.