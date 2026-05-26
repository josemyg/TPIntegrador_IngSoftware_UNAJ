from django.db import models
from django.utils import timezone
from gestion.models import TipoCancha
#from gestion.models import Usuario


class Reserva(models.Model):
    # Atributos básicos
    cliente = models.ForeignKey('gestion.Usuario', on_delete=models.CASCADE, verbose_name="Cliente")
    tipo_cancha = models.ForeignKey(TipoCancha, on_delete=models.CASCADE, verbose_name="Tipo de Cancha")
    fecha = models.DateField(verbose_name="Fecha de la reserva")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")

    # Atributos de gestión
    estado = models.CharField(max_length=20, default='PENDIENTE', choices=[('PENDIENTE', 'Pendiente'), ('CONFIRMADA', 'Confirmada'), ('CANCELADA', 'Cancelada')])
    precio_final = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # --- Métodos (Lógica) ---

    #def calcular_precio(self):
        # Lógica: (hora_fin - hora_inicio) * precio_por_hora de la cancha
        # Implementar la lógica de descuentos
     #   pass

    #def es_cancelable(self):
        # Regla: 6 horas de antelación
    #    tiempo_limite = timezone.now() + timezone.timedelta(hours=6)
        # Comparar con la fecha/hora de la reserva
     #   return timezone.now() < tiempo_limite

    def clean(self):
        # Aquí llamarías a tus métodos de validación antes de guardar
        super().clean()

    def __str__(self):
        return f"Reserva de {self.cliente} para el {self.fecha}"