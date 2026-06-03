from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.utils.timezone import now as Now

class TipoPago(models.Model):
    nombre = models.CharField(max_length=50) # Efectivo, Transferencia, Débito, etc.
    estado = models.CharField(max_length=20, default='activo')

    def __str__(self):
        return self.nombre

class Pago(models.Model):
    ORIGEN_CHOICES = [
        ('alquiler_cancha', 'Alquiler de Cancha'),
        ('inscripcion_liga', 'Inscripción a Liga'),
        ('inscripcion_torneo', 'Inscripción a Torneo'),
        ('otros_servicios', 'Otros Servicios'),
    ]

    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    # Relación con la app de reservas de tu compañero (Corregimos a string 'reservas.Reserva' para evitar importación circular)
    reserva = models.ForeignKey(
        'reservas.Reserva',
        on_delete=models.PROTECT,
        related_name='pagos', # En plural es mejor práctica para el reverse lookup
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_PAGO,
        default='PENDIENTE'
    )

    origen_pago = models.CharField(max_length=30, choices=ORIGEN_CHOICES)
    
    monto = models.FloatField(null=True, blank=True) 
    
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.PROTECT, null=True, blank=True)
    
    fecha = models.DateField(auto_now_add=True)

    descuento = models.ForeignKey('descuentos.Descuento', on_delete=models.PROTECT, null=True, blank=True)

    @property
    def valor_descuento(self):
        """Calcula cuántos pesos representa el descuento aplicado"""
        if self.monto and self.descuento and getattr(self.descuento, 'cantidad', None):
            try:
                porcentaje_num = float(self.descuento.cantidad)
                return round((self.monto * porcentaje_num) / 100.0, 2)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    @property
    def monto_final(self):
        """Calcula el monto neto restando los pesos del descuento si existe"""
        if self.monto:
            return round(self.monto - self.valor_descuento, 2)
        return 0.0

    def __str__(self):
        # Un fix por si se lista un pago que todavía no tiene el monto asignado
        monto_str = f"${self.monto}" if self.monto else "Sin Monto Asignado"
        return f"Pago #{self.id} - {self.get_origen_pago_display()} ({monto_str}) - [{self.get_estado_display()}]"


class Recibo(models.Model):
    fecha = models.DateTimeField(auto_now=False, auto_now_add=False)
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='recibo')

    def __str__(self):
        return f"Recibo #{self.id} (Pago #{self.pago.id})"
    

@receiver(post_save, sender=Pago)
def crear_Recibo(sender, instance, created, **kwargs):
    if created:
        pago = instance
        recibo = Recibo.objects.create(pago=pago, fecha=Now())
        recibo.save()
        instance.recibo = recibo
        print("Recibo creado correctamente")
