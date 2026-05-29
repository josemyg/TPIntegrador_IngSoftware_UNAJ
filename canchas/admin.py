from django.contrib import admin
from .models import TipoCancha  # 👈 Importamos tu modelo

# 👈 Registramos el modelo en el panel de control de Django
admin.site.register(TipoCancha)
