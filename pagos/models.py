from django.db import models

class TipoPago(models.Model):
    nombre = models.CharField(max_length=50) # Efectivo, Transferencia, Débito, etc.
    estado = models.CharField(max_length=20, default='activo')

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    # Definimos los tipos de servicios de tus Requerimientos Funcionales
    ORIGEN_CHOICES = [
        ('alquiler_cancha', 'Alquiler de Cancha'),
        ('inscripcion_liga', 'Inscripción a Liga'),
        ('inscripcion_torneo', 'Inscripción a Torneo'),
        ('otros_servicios', 'Otros Servicios'),
    ]

    reserva = models.OneToOneField(
        'reservas.Reserva',
        on_delete=models.CASCADE,
        related_name='pago'
    )

    ESTADOS_PAGO = [
    ('PENDIENTE', 'Pendiente'),
    ('PAGADO', 'Pagado'),
    ('RECHAZADO', 'Rechazado'),
]

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_PAGO,
        default='PENDIENTE'
    )

    monto = models.FloatField()
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.PROTECT)
    fecha = models.DateField(auto_now_add=True)
    descuento = models.ForeignKey('descuentos.Descuento', on_delete=models.SET_NULL, null=True, blank=True)
    origen_pago = models.CharField(max_length=30, choices=ORIGEN_CHOICES)

    @property
    def monto_final(self):
        """Calcula el monto neto restando el porcentaje si existe, sino devuelve el bruto"""
        # Validamos estrictamente que exista el descuento Y que tenga un porcentaje válido
        if self.descuento and getattr(self.descuento, 'cantidad', None):
            try:
                porcentaje_num = float(self.descuento.cantidad)
                descuento_aplicado = (self.monto * porcentaje_num) / 100.0
                return round (self.monto - descuento_aplicado, 2)
            except (ValueError, TypeError):
                return self.monto  # Por si el porcentaje no era un número válido
        
        # Si no hay descuento, el monto final es exactamente el monto bruto original
        return self.monto

    def __str__(self):
        return f"Pago #{self.id} - {self.get_origen_pago_display()} (${self.monto})"


class Recibo(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE)

    def __str__(self):
        return f"Recibo #{self.id} (Pago #{self.pago.id})"
    