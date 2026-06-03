from django.db import models
from django.utils import timezone
from canchas.models import TipoCancha
#from gestion.models import Usuario

class Reserva(models.Model):

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ] # Define los posibles estados de una reserva: pendiente, confirmada o cancelada.

    cliente = models.ForeignKey(
        'gestion.Usuario',
        on_delete=models.PROTECT,
        verbose_name="Cliente"
    ) # Relación de clave foránea con el modelo Usuario, que representa al cliente que realiza la reserva. on_delete=models.CASCADE significa que si el cliente es eliminado, también se eliminarán sus reservas asociadas. verbose_name se utiliza para mostrar un nombre legible en el panel de administración de Django.

    tipo_cancha = models.ForeignKey(
        TipoCancha,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Cancha"
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

        inicio = self.hora_inicio.hour
        fin = self.hora_fin.hour

        horas = fin - inicio

        self.precio_final = horas * self.tipo_cancha.precio_hora # Calcula el precio final multiplicando la cantidad de horas reservadas por el precio por hora del tipo de cancha seleccionado.

    def save(self, *args, **kwargs):

        self.calcular_precio()

        super().save(*args, **kwargs) # Sobrescribe el método save para calcular el precio final antes de guardar la reserva en la base de datos. Llama al método calcular_precio para actualizar el campo precio_final y luego llama al método save original de la clase padre para guardar la reserva.

    def __str__(self):
        return f"{self.cliente} - {self.fecha}" # Sobrescribe el método __str__ para mostrar el nombre del cliente y la fecha de la reserva en la representación de cadena de la reserva. Esto es útil para identificar fácilmente las reservas en el panel de administración y en otros lugares donde se muestre la reserva como texto.
