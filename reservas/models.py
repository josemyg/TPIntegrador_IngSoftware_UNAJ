from datetime import date, datetime
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from canchas.models import Cancha, TipoCancha
from pagos.models import Pago, TipoPago

class Reserva(models.Model):

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ] # Define los posibles estados de una reserva: pendiente, confirmada o cancelada.

    cliente = models.ForeignKey(
        'gestion.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cliente"
    )       # Campo de clave foránea que se relaciona con el modelo Usuario de la aplicación de gestión, con una restricción de eliminación en cascada para proteger los datos relacionados y un nombre legible en el panel de administración.

    cancha = models.ForeignKey(
        'canchas.Cancha',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Cancha"
    )

    fecha = models.DateField(verbose_name="Fecha de la reserva") # Campo de fecha para la reserva, con un nombre legible en el panel de administración.

    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE'
    ) # Campo de texto para el estado de la reserva, con opciones limitadas a las definidas en ESTADOS y un valor predeterminado de 'PENDIENTE'.

    precio_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    ) # Campo decimal para almacenar el precio final de la reserva, con un máximo de 10 dígitos y 2 decimales, y un valor predeterminado de 0.00.

    fecha_creacion = models.DateTimeField(auto_now_add=True) # Campo de fecha y hora que se establece automáticamente al crear una nueva reserva, para llevar un registro de cuándo se realizó la reserva.

    def calcular_precio(self):

        fecha = date.today()
        # Combina la fecha actual con la hora de inicio de la reserva para obtener un objeto datetime que representa el momento en que comienza la reserva.
        dt_inicio = datetime.combine(fecha, self.hora_inicio)
        # Combina la fecha actual con la hora de fin de la reserva para obtener un objeto datetime que representa el momento en que termina la reserva.
        dt_fin = datetime.combine(fecha, self.hora_fin)
        diferencia = (dt_fin - dt_inicio).total_seconds() / 3600  # Horas en decimal
        # Calcula el precio final multiplicando la cantidad de horas reservadas por el precio por hora del tipo de cancha seleccionado.
        self.precio_final = diferencia * float(self.cancha.tipo.precio_hora)

    def save(self, *args, **kwargs):

        self.calcular_precio()

        super().save(*args, **kwargs) # Sobrescribe el método save para calcular el precio final antes de guardar la reserva en la base de datos. Llama al método calcular_precio para actualizar el campo precio_final y luego llama al método save original de la clase padre para guardar la reserva.

    def __str__(self):
        return f"{self.cliente} - {self.fecha}" # Sobrescribe el método __str__ para mostrar el nombre del cliente y la fecha de la reserva en la representación de cadena de la reserva. Esto es útil para identificar fácilmente las reservas en el panel de administración y en otros lugares donde se muestre la reserva como texto.



@receiver(post_save, sender=Reserva)
def crear_pago_automatico(sender, instance, created, **kwargs):
    if created:
        tipo_pago = TipoPago.objects.filter(nombre='Efectivo').first()
        if not tipo_pago:
            tipo_pago = TipoPago.objects.create(nombre='Efectivo', estado='activo')

        Pago.objects.create(
            reserva=instance,
            monto=instance.precio_final,
            estado='PENDIENTE',
            tipo_pago=tipo_pago,
            origen_pago='alquiler_cancha',
        )

@receiver(post_save, sender=Pago)
def actualizar_estado_reserva(sender, instance, **kwargs):

    reserva = instance.reserva

    nuevo_estado = reserva.estado

    if instance.estado == 'PAGADO':
        nuevo_estado = 'CONFIRMADA'

    elif instance.estado == 'RECHAZADO':
        nuevo_estado = 'CANCELADA'

    elif instance.estado == 'PENDIENTE':
        nuevo_estado = 'PENDIENTE'

    if reserva.estado != nuevo_estado:
        reserva.estado = nuevo_estado
        reserva.save(update_fields=['estado'])