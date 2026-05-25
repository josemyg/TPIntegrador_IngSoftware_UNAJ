from django.db import models

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete


class Usuario(models.Model):

    id = models.AutoField("ID Usuario", primary_key=True)
    nombre = models.CharField(("Nombre/s"), max_length=100)
    apellido = models.CharField(("Apellido/s"), max_length=100)
    direccion = models.CharField(("Dirección"), max_length=200)
    localidad = models.CharField(("Localidad"), max_length=60)
    provincia = models.CharField(("Provincia"), max_length=60)
    pais = models.CharField(("Pais"), max_length=50)
    cpa = models.CharField(("CPA"), max_length=20)
    nacionalidad = models.CharField(("Nacionalidad"), max_length=50)
    telefono = models.CharField(("Teléfono"), max_length=20)
    email = models.EmailField(("Correo Electrónico"), max_length=254)
    dni = models.CharField(("DNI"), max_length=20)
    user_django = models.OneToOneField(
        User,
        on_delete = models.PROTECT,
        verbose_name = ('Usuario'),
        blank = True,
        null = True
        )

    class Meta:
        verbose_name = ("Usuario")
        verbose_name_plural = ("Usuarios")

    def __str__(self):
        if self.nombre and self.apellido:
            return self.nombre + ' ' + self.apellido
        else:
            return 'Sin nombre'

    def get_absolute_url(self):
        return reverse("Usuario_detail", kwargs={"pk": self.pk})

    def registrarUsuario():
        return self.nombre

    def modificarUsuario():
        return self.nombre


class Profesor(Usuario):

    estados = {
    'activo': 'Activo',
    'inactivo': 'Inactivo',
    'baja': 'Baja',
    'en_validación':'En espera de Validación',
    }

    titulo_habilitante = models.CharField(("Título Habilitante"), max_length=100)
    institucion_habilitante = models.CharField(("Institución Habilitante"), max_length=100)
    certificado = models.FileField(("Certificado"), upload_to='archivo/certificados', max_length=100)
    estado = models.CharField(("Estado"), choices=estados, default='en_validación', max_length=50)

    class Meta:
        verbose_name = ("Profesor/a")
        verbose_name_plural = ("Profesores")

@receiver(post_save, sender=Profesor)
def crear_Usuario(sender, instance, created, **kwargs):
    if created:
        nombre = instance.nombre+'_'+instance.apellido
        print(nombre)
        user = User.objects.create_user(nombre,instance.email, 'f.123456')
        user.save()
        instance.user_django = user
        print("Se ha creado el perfil de usuario correctamente")