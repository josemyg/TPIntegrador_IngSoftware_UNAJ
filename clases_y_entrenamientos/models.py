from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from gestion.models import Cliente, Profesor
from django.utils import timezone
from django.utils.timezone import localtime


class Clase(models.Model):
    id = models.AutoField("ID Clase", primary_key=True)
    nombre = models.CharField(("Nombre"), max_length=100)
    horario = models.DateTimeField(("Horario"))
    cupo_maximo = models.PositiveIntegerField(default=10)
    ESTADO_OPCIONES = [
        ('programada', 'Programada'),
        ('en_curso', 'En curso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(
        max_length=20, choices=ESTADO_OPCIONES, default='programada')
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name='clases',
        blank=True,
        null=True
    )
    alumnos = models.ManyToManyField(
        Cliente,
        related_name='clases',
        blank=True
    )

    class Meta:
        verbose_name = "Clase"
        verbose_name_plural = "Clases"
        ordering = ['horario']

    def __str__(self):
        if self.nombre and self.horario:
            return self.nombre + ' ' + localtime(self.horario).strftime('%d/%m/%Y %H:%M')
        else:
            return 'Clase sin nombre'

    @classmethod
    def crear_clase(cls, nombre, horario, cupo_maximo, profesor, alumnos=None):
        if alumnos is not None and len(alumnos) > cupo_maximo:
            raise ValueError('El número de alumnos excede el cupo máximo.')

        clase = cls(
            nombre=nombre,
            horario=horario,
            cupo_maximo=cupo_maximo,
            profesor=profesor
        )
        clase.save()
        if alumnos is not None:
            clase.alumnos.set(alumnos)
        return clase

    def modificar_clase(self, **datos):
        if 'alumnos' in datos and datos['alumnos'] is not None:
            cupo = datos.get('cupo_maximo', self.cupo_maximo)
            if len(datos['alumnos']) > cupo:
                raise ValueError('El número de alumnos excede el cupo máximo.')

        for key, value in datos.items():
            if hasattr(self, key) and key not in ['id', 'alumnos']:
                setattr(self, key, value)

        self.save()
        if 'alumnos' in datos:
            self.alumnos.set(datos['alumnos'])
        return self

    def eliminar_clase(self):
        self.delete()

    def consultar_clase(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
            'profesor': str(self.profesor) if self.profesor else 'Sin profesor',
            'cupo_maximo': self.cupo_maximo,
            'inscriptos': self.alumnos.count(),
            'alumnos': [{'id': a.id, 'nombre': str(a)} for a in self.alumnos.all()],
            'estado': self.estado,
        }

    def imprimir_clase(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
            'profesor': str(self.profesor) if self.profesor else 'Sin profesor',
            'cupo_maximo': self.cupo_maximo,
            'inscriptos': self.alumnos.count(),
            'alumnos': [{'id': a.id, 'nombre': str(a)} for a in self.alumnos.all()],
            'estado': self.estado,
            'fecha_impresion': localtime(timezone.now()).strftime('%d/%m/%Y %H:%M:%S')
        }

    def generar_reporte_clase(self):
        asistencias = self.asistencias_clase.all().select_related('alumno')
        total_inscriptos = self.alumnos.count()
        total_registros = asistencias.count()
        presentes = asistencias.filter(asistencia=True).count()
        ausentes = total_registros - presentes
        porcentaje = (presentes / total_inscriptos *
                      100) if total_inscriptos > 0 else 0

        return {
            'clase': {
                'id': self.id,
                'nombre': self.nombre,
                'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
                'profesor': str(self.profesor) if self.profesor else 'Sin profesor',
                'cupo_maximo': self.cupo_maximo,
                'inscriptos': total_inscriptos,
                'estado': self.estado,
            },
            'resumen_asistencia': {
                'total_registros': total_registros,
                'presentes': presentes,
                'ausentes': ausentes,
                'porcentaje_asistencia': round(porcentaje, 2)
            },
            'detalle_asistencia': [
                {
                    'alumno': str(a.alumno),
                    'asistencia': a.asistencia,

                } for a in asistencias
            ],
            'fecha_reporte': localtime(timezone.now()).strftime('%d/%m/%Y %H:%M:%S')
        }

    def generar_reporte_asistencia(self):
        asistencias = self.asistencias_clase.all().select_related('alumno')
        total_registros = asistencias.count()
        presentes = asistencias.filter(asistencia=True).count()
        return {
            'clase': self.nombre,
            'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
            'total_alumnos_inscriptos': self.alumnos.count(),
            'total_registros_asistencia': total_registros,
            'presentes': presentes,
            'ausentes': total_registros - presentes,
            'detalle': [{'alumno': str(a.alumno), 'asistencia': a.asistencia} for a in asistencias],
        }

    def asignar_profesor(self, nuevo_profesor):
        self.profesor = nuevo_profesor
        self.save()

    def eliminar_profesor(self):
        self.profesor = None
        self.save()

    def asignar_alumno(self, cliente):
        if self.alumnos.count() < self.cupo_maximo:
            self.alumnos.add(cliente)
            self.save()
            return True
        return False

    def eliminar_alumno(self, cliente):
        if cliente in self.alumnos.all():
            self.alumnos.remove(cliente)
            self.save()
            return True
        return False

    def definir_cupo_maximo(self, nuevo_cupo):
        self.cupo_maximo = nuevo_cupo
        self.save()

    def verificar_cupo(self):
        if self.alumnos.count() < self.cupo_maximo:
            return True
        return False


class Entrenamiento(models.Model):
    id = models.AutoField("ID Entrenamiento", primary_key=True)
    nombre = models.CharField(("Nombre"), max_length=100)
    horario = models.DateTimeField(("Horario"))
    cupo_maximo = models.PositiveIntegerField(default=10)
    ESTADO_OPCIONES = [
        ('programado', 'Programado'),
        ('en_curso', 'En curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(
        max_length=20, choices=ESTADO_OPCIONES, default='programado')
    entrenador = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name='entrenamientos',
        blank=True,
        null=True
    )
    alumnos = models.ManyToManyField(
        Cliente,
        related_name='entrenamientos',
        blank=True,
    )

    class Meta:
        verbose_name = "Entrenamiento"
        verbose_name_plural = "Entrenamientos"
        ordering = ['horario']

    def __str__(self):
        if self.nombre and self.horario:
            return self.nombre + ' ' + localtime(self.horario).strftime('%d/%m/%Y %H:%M')
        else:
            return 'Entrenamiento sin nombre'

    @classmethod
    def crear_entrenamiento(cls, nombre, horario, cupo_maximo, entrenador, alumnos=None):
        if alumnos is not None and len(alumnos) > cupo_maximo:
            raise ValueError('El número de alumnos excede el cupo máximo.')

        ent = cls(
            nombre=nombre,
            horario=horario,
            cupo_maximo=cupo_maximo,
            entrenador=entrenador
        )
        ent.save()
        if alumnos is not None:
            ent.alumnos.set(alumnos)
        return ent

    def modificar_entrenamiento(self, **datos):
        if 'alumnos' in datos and datos['alumnos'] is not None:
            cupo = datos.get('cupo_maximo', self.cupo_maximo)
            if len(datos['alumnos']) > cupo:
                raise ValueError('El número de alumnos excede el cupo máximo.')

        for key, value in datos.items():
            if hasattr(self, key) and key not in ['id', 'alumnos']:
                setattr(self, key, value)

        self.save()
        if 'alumnos' in datos:
            self.alumnos.set(datos['alumnos'])
        return self

    def consultar_entrenamiento(self):

        return {
            'id': self.id,
            'nombre': self.nombre,
            'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
            'entrenador': str(self.entrenador) if self.entrenador else 'Sin entrenador',
            'cupo_maximo': self.cupo_maximo,
            'inscriptos': self.alumnos.count(),
            'alumnos': [{'id': a.id, 'nombre': str(a)} for a in self.alumnos.all()],
            'estado': self.estado,
        }

    def imprimir_entrenamiento(self):

        return {
            'id': self.id,
            'nombre': self.nombre,
            'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
            'entrenador': str(self.entrenador) if self.entrenador else 'Sin entrenador',
            'cupo_maximo': self.cupo_maximo,
            'inscriptos': self.alumnos.count(),
            'alumnos': [{'id': a.id, 'nombre': str(a)} for a in self.alumnos.all()],
            'estado': self.estado,
            'fecha_impresion': localtime(timezone.now()).strftime('%d/%m/%Y %H:%M:%S')
        }

    def generar_reporte_entrenamiento(self):
        asistencias = self.asistencias_entrenamiento.all().select_related('alumno')
        total_inscriptos = self.alumnos.count()
        total_registros = asistencias.count()
        presentes = asistencias.filter(asistencia=True).count()
        ausentes = total_registros - presentes
        porcentaje = (presentes / total_inscriptos *
                      100) if total_inscriptos > 0 else 0

        return {
            'entrenamiento': {
                'id': self.id,
                'nombre': self.nombre,
                'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
                'entrenador': str(self.entrenador) if self.entrenador else 'Sin entrenador',
                'cupo_maximo': self.cupo_maximo,
                'inscriptos': total_inscriptos,
                'estado': self.estado,
            },
            'resumen_asistencia': {
                'total_registros': total_registros,
                'presentes': presentes,
                'ausentes': ausentes,
                'porcentaje_asistencia': round(porcentaje, 2)
            },
            'detalle_asistencia': [
                {
                    'alumno': str(a.alumno),
                    'asistencia': a.asistencia,

                } for a in asistencias
            ],
            'fecha_reporte': localtime(timezone.now()).strftime('%d/%m/%Y %H:%M:%S')
        }

    def eliminar_entrenamiento(self):
        self.delete()

    def generar_reporte_asistencia(self):
        """Reporte de asistencia para este entrenamiento."""
        asistencias = self.asistencias_entrenamiento.all().select_related('alumno')
        total_registros = asistencias.count()
        presentes = asistencias.filter(asistencia=True).count()
        return {
            'entrenamiento': self.nombre,
            'horario': localtime(self.horario).strftime('%d/%m/%Y %H:%M'),
            'total_alumnos_inscriptos': self.alumnos.count(),
            'total_registros_asistencia': total_registros,
            'presentes': presentes,
            'ausentes': total_registros - presentes,
            'detalle': [{'alumno': str(a.alumno), 'asistencia': a.asistencia} for a in asistencias],
        }

    def asignar_entrenador(self, nuevo_entrenador):
        self.entrenador = nuevo_entrenador
        self.save()

    def eliminar_entrenador(self):
        self.entrenador = None
        self.save()

    def asignar_alumno(self, cliente):
        if self.alumnos.count() < self.cupo_maximo:
            self.alumnos.add(cliente)
            self.save()
            return True
        return False

    def eliminar_alumno(self, cliente):
        if cliente in self.alumnos.all():
            self.alumnos.remove(cliente)
            self.save()
            return True
        return False

    def definir_cupo_maximo(self, nuevo_cupo):
        self.cupo_maximo = nuevo_cupo
        self.save()

    def verificar_cupo(self):
        if self.alumnos.count() < self.cupo_maximo:
            return True
        return False


class AsistenciaClase(models.Model):
    clase = models.ForeignKey(
        'Clase', on_delete=models.CASCADE, related_name='asistencias_clase')
    alumno = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    asistencia = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Asistencia a clase"
        verbose_name_plural = "Asistencias a clases"
        unique_together = ('clase', 'alumno')

    def __str__(self):
        return f"{self.alumno} - {self.clase.nombre} - {'Presente' if self.asistencia else 'Ausente'}"

    @classmethod
    def generar_asistencia(cls, clase, alumno, asistencia=False):
        obj, created = cls.objects.get_or_create(
            clase=clase,
            alumno=alumno,
            defaults={'asistencia': asistencia}
        )
        if not created:
            obj.asistencia = asistencia
            obj.save()
        return obj

    def modificar_asistencia(self, nuevo_estado):
        self.asistencia = nuevo_estado
        self.save()

    def eliminar_asistencia(self):
        self.delete()

    def consultar_asistencia(self):
        return {
            'id': self.id,
            'alumno': str(self.alumno),
            'asistencia': self.asistencia,
        }

    def generar_reporte_asistencia(self):
        reporte = self.consultar_asistencia()
        reporte.update({
            'tipo': 'clase',
            'clase_nombre': self.clase.nombre,
            'clase_horario': localtime(self.clase.horario).strftime('%d/%m/%Y %H:%M'),
            'profesor': str(self.clase.profesor) if self.clase.profesor else 'Sin profesor',
            'fecha_reporte': localtime(timezone.now()).strftime('%d/%m/%Y %H:%M'),
        })
        return reporte


class AsistenciaEntrenamiento(models.Model):
    entrenamiento = models.ForeignKey(
        'Entrenamiento', on_delete=models.CASCADE, related_name='asistencias_entrenamiento')
    alumno = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    asistencia = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Asistencia a entrenamiento"
        verbose_name_plural = "Asistencias a entrenamientos"
        unique_together = ('entrenamiento', 'alumno')

    def __str__(self):
        return f"{self.alumno} - {self.entrenamiento.nombre} - {'Presente' if self.asistencia else 'Ausente'}"

    @classmethod
    def generar_asistencia(cls, entrenamiento, alumno, asistencia=False):
        obj, created = cls.objects.get_or_create(
            entrenamiento=entrenamiento,
            alumno=alumno,
            defaults={'asistencia': asistencia}
        )
        if not created:
            obj.asistencia = asistencia
            obj.save()
        return obj

    def modificar_asistencia(self, nuevo_estado):
        self.asistencia = nuevo_estado
        self.save()

    def eliminar_asistencia(self):
        self.delete()

    def consultar_asistencia(self):
        return {
            'id': self.id,
            'alumno': str(self.alumno),
            'asistencia': self.asistencia,
        }

    def generar_reporte_asistencia(self):
        reporte = self.consultar_asistencia()
        reporte.update({
            'tipo': 'entrenamiento',
            'entrenamiento_nombre': self.entrenamiento.nombre,
            'entrenamiento_horario': localtime(self.entrenamiento.horario).strftime('%d/%m/%Y %H:%M'),
            'entrenador': str(self.entrenamiento.entrenador) if self.entrenamiento.entrenador else 'Sin entrenador',
            'fecha_reporte': localtime(timezone.now()).strftime('%d/%m/%Y %H:%M'),
        })
        return reporte
