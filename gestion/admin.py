from django.contrib import admin

# Register your models here.
from .models import Cliente, Profesor

admin.site.register(Cliente)
admin.site.register(Profesor)

""" @admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ['nombre', 'apellido', 'dni'] 

    list_display = ['nombre', 'apellido', 'dni', 'email'] """