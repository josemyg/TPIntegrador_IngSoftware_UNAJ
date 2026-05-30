from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

# Create your models here.
class Descuento(models.Model):


    tiposDescuentos=[
        ('socio', 'Socio del club'),
        ('empleado', 'Empleado'),
        ('temporal', 'Promoción temporal'),
        ('torneo', 'Torneo'),
    ]

    estados = [
    ('activo', 'Activo'),
    ('programado', 'Programado'),
    ('vencido', 'Vencido'),
    ('suspendido', 'Suspendido'),
    ('baja', 'Baja'),
    ]

    tipo = models.CharField(("Tipo"), choices=tiposDescuentos, max_length=50)

    cantidad=models.DecimalField(max_digits=5, decimal_places=2)

    estado = models.CharField(("Estado"), choices=estados,default="activo",max_length=50)


    class Meta:
        verbose_name = ("Descuento")
        verbose_name_plural = ("Descuentos")


    def descuento_Activo(self):
        return self.estado=="activo"

    def darDescuento_Baja(self):
        self.estado="baja"
        self.save()    

    def __str__(self):
     return f"{self.get_tipo_display()} - {self.cantidad}%"