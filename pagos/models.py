from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.utils.timezone import now as Now
from descuentos.models import Descuento

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

    descuento = models.ForeignKey(Descuento, on_delete=models.PROTECT, null=True, blank=True)


    @property
    def monto_bruto(self):
        """Calcula el monto original antes de aplicar el descuento."""
        if self.monto and self.descuento and getattr(self.descuento, 'cantidad', None):
            try:
                porcentaje_num = float(self.descuento.cantidad)
                if porcentaje_num >= 100:
                    return round(self.monto, 2)
                bruto = self.monto / (1 - porcentaje_num / 100.0)
                return round(bruto, 2)
            except (ValueError, TypeError, ZeroDivisionError):
                return round(self.monto, 2)
        return round(self.monto or 0.0, 2)
    
    @property
    def valor_descuento(self):
        """Calcula cuántos pesos representa el descuento aplicado."""
        if self.monto is None or not self.descuento or not getattr(self.descuento, 'cantidad', None):
            return 0.0

        try:
            bruto = self.monto_bruto
            return round(bruto - self.monto, 2)
        except (ValueError, TypeError):
            return 0.0


    def calcular_monto_con_descuento(self, monto_base=None):
        """Devuelve el monto después de aplicar el descuento en porcentaje."""
        if monto_base is None:
            monto_base = self.monto or 0.0
        try:
            monto_base = float(monto_base)
        except (ValueError, TypeError):
            return 0.0

        if self.descuento and getattr(self.descuento, 'cantidad', None):
            try:
                porcentaje_num = float(self.descuento.cantidad)
                descuento_calculado = (monto_base * porcentaje_num) / 100.0
                return round(monto_base - descuento_calculado, 2)
            except (ValueError, TypeError):
                return round(monto_base, 2)

        return round(monto_base, 2)



    @property
    def monto_final(self):
        """Devuelve el monto final cobrado."""
        return round(self.monto or 0.0, 2)

    def __str__(self):
        # Un fix por si se lista un pago que todavía no tiene el monto asignado
        monto_str = f"${self.monto}" if self.monto else "Sin Monto Asignado"
        return f"Pago #{self.id} - {self.get_origen_pago_display()} ({monto_str}) - [{self.get_estado_display()}]"
    
    
class Recibo(models.Model):
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    pago = models.OneToOneField(Pago, on_delete=models.PROTECT, related_name='recibo')

    def __str__(self):
        return f"Recibo #{self.id} (Pago #{self.pago.id})"
    

@receiver(post_save, sender=Pago)
def crear_Recibo(sender, instance, created, **kwargs):
    if instance.estado == 'PAGADO':
        # 1. Creamos el recibo si no existe todavía usando la relación reversa
        if not hasattr(instance, 'recibo'): # Verificamos si el pago ya tiene un recibo asociado para evitar crear duplicados
            Recibo.objects.create(pago=instance)
            print(f"Recibo creado automáticamente para el Pago #{instance.id}")

        # 2. Si el pago tiene una reserva asociada, la confirmamos automáticamente
        if instance.reserva and instance.reserva.estado != 'CONFIRMADA':
            instance.reserva.estado = 'CONFIRMADA'
            instance.reserva.save()
            print(f"Reserva #{instance.reserva.id} confirmada automáticamente")