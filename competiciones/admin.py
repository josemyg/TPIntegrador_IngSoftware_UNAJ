from django.contrib import admin

# Register your models here.
from .models import Equipo, Liga, Torneo, Partido

admin.site.register(Equipo)
admin.site.register(Liga)
admin.site.register(Torneo)
admin.site.register(Partido)
