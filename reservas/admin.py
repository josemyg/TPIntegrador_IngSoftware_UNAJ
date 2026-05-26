from django.contrib import admin
from .models import Reserva



@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_cancha', 'fecha', 'hora_inicio', 'estado', 'precio_final')
    list_filter = ('fecha', 'estado', 'tipo_cancha')
    # Esto te permite buscar al cliente por sus campos en gestion/models.py
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__dni') 
    autocomplete_fields = ['cliente'] # Esto requiere que 'cliente' tenga search_fields en su admin [cite: 1210, 1211]