from django.contrib import admin
from .models import Clase, Entrenamiento , AsistenciaClase, AsistenciaEntrenamiento

admin.site.register(Clase)
admin.site.register(Entrenamiento)
admin.site.register(AsistenciaClase) 
admin.site.register(AsistenciaEntrenamiento) 
