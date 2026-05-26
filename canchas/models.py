from django.db import models

class TipoCancha(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Tipo de Cancha")
    capacidad = models.IntegerField(verbose_name="Capacidad (Jugadores)")
    superficie = models.CharField(max_length=100, verbose_name="Superficie")
    def __str__(self):
        return f"{self.nombre} - {self.superficie}"
    
    class Meta:
        verbose_name = "Tipo de Cancha"
        verbose_name_plural = "Tipos de Canchas"