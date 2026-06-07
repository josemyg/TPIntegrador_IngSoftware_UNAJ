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

    nombreTipo = models.CharField(max_length=100, verbose_name="Tipo de Cancha")

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

    max_horas = models.PositiveIntegerField(
        default=2, 
        verbose_name="Máximo de horas por reserva",
        help_text="Cantidad máxima de horas seguidas que se puede alquilar este tipo de cancha."
    )

    def __str__(self):
        return f"{self.nombreTipo} - {self.get_superficie_display()} - ${self.precio_hora}/hora"
    
    class Meta:
        verbose_name = "Tipo de Cancha"
        verbose_name_plural = "Tipos de Canchas"


class Cancha(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo / Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
        ('inactivo', 'Inactivo'),
    ]

    nombre = models.CharField(
        max_length=100, 
        verbose_name="Nombre de la Cancha",
        help_text="Ej: Cancha N° 1 Techada"
    )
    
    # 🔗 Relación con TipoCancha (La flecha de tu diagrama)
    tipo = models.ForeignKey(TipoCancha, on_delete=models.PROTECT, related_name='canchas')
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Disponible'
    )

    def __str__(self):
        return f"{self.nombre} / {self.tipo.nombreTipo} / {self.tipo.get_superficie_display()} / {self.tipo.capacidad } jugadores"

    def consultarDisponibilidad(self, fecha, hora_inicio):
        # lógica para consultar si la cancha está disponible en esa fecha y hora
        pass

    def activarCancha(self):
        """Cambia el estado de vuelta a DISPONIBLE"""
        self.estado = 'DISPONIBLE'
        self.save()

    def bloquearReservas(self):
        self.estado = 'MANTENIMIENTO'
        self.save()
   

    def consultarCancha(self):
        return f"Cancha: {self.nombre} - Tipo: {self.tipo.nombre} - Estado: {self.estado}"