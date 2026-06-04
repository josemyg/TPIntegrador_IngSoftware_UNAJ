from django.contrib import admin

# Register your models here.
from .models import Usuario, Profesor, TipoCancha

admin.site.register(Profesor)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ['nombre', 'apellido', 'dni'] 

    list_display = ['nombre', 'apellido', 'dni', 'email']

admin.site.register(TipoCancha)