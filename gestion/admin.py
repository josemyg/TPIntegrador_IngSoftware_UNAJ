from django.contrib import admin

# Register your models here.
from .models import Usuario, Profesor, Cliente


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
	search_fields = ('nombre', 'apellido', 'dni')


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
	search_fields = ('nombre', 'apellido', 'dni')

try:
	@admin.register(Cliente)
	class ClienteAdmin(admin.ModelAdmin):
		search_fields = ('nombre', 'apellido', 'dni')
except Exception:
	# Cliente may not be defined in some states; fallback to safe register
	try:
		admin.site.register(Cliente)
	except Exception:
		pass