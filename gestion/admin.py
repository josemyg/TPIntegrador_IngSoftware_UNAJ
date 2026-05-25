from django.contrib import admin

# Register your models here.
from .models import Usuario, Profesor

admin.site.register(Usuario)
admin.site.register(Profesor)