from django.db import models

class TipoCancha(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo / Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
        ('inactivo', 'Inactivo'),
    ]
    SUPERFICIE_CHOICES = [
        ('cesped_natural','Césped Natural'),
        ('sintetico','Césped Sintético'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Tipo de Cancha")

    capacidad = models.IntegerField(verbose_name="Capacidad (Jugadores)")

    superficie = models.CharField(
        max_length=50, 
        choices=SUPERFICIE_CHOICES, 
        default='sintetico', 
        verbose_name="Superficie"
    )
    precio_hora = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio por Hora",
        default=0
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='activo', 
        verbose_name="Estado"
    )

    def __str__(self):
        return f"{self.nombre} - {self.get_superficie_display()}"
    
    class Meta:
        verbose_name = "Tipo de Cancha"
        verbose_name_plural = "Tipos de Canchas"