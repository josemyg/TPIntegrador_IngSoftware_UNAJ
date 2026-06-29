from django.db import models
from gestion.models import Profesor, Cliente
from canchas.models import Cancha


# ==========================================
# 2. MODELO DE EQUIPO
# ==========================================
class Equipo(models.Model):
    nombre = models.CharField("Nombre del Equipo", max_length=100, unique=True)
    profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Profesor Asignado")
    clientes = models.ManyToManyField(Cliente, blank=True, verbose_name="Integrantes (Maximo 15)")

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"

    def __str__(self):
        return self.nombre


# ==========================================
# 3. MODELOS DE COMPETICIONES (Ligas y Torneos)
# ==========================================
class Competicion(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, default='Inscripcion', choices=[
        ('Inscripcion', 'En Inscripcion'),
        ('En_Curso', 'En Curso'),
        ('Finalizada', 'Finalizada')
    ])
    equipos = models.ManyToManyField(Equipo, related_name='competiciones', blank=True)

    class Meta:
        verbose_name = "Competicion"
        verbose_name_plural = "Competiciones"

    def __str__(self):
        return self.nombre

class Liga(Competicion):
    puntos_victoria = models.IntegerField(default=3)
    puntos_empate = models.IntegerField(default=1)
    es_ida_y_vuelta = models.BooleanField(default=False, verbose_name="Partidos de ida y vuelta")

    class Meta:
        verbose_name = "Liga"
        verbose_name_plural = "Ligas"

class Torneo(Competicion):
    es_ida_y_vuelta = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Torneo"
        verbose_name_plural = "Torneos"


# =================================
# 4.     EL MODELO DE PARTIDO     =      
# =================================

class Partido(models.Model):
    competicion = models.ForeignKey(Competicion, on_delete=models.CASCADE, related_name='partidos')
    equipo_local = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name='partidos_local')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name='partidos_visitante')
    
    # Vinculado a la Cancha (Temporal) de arriba
    cancha_asignada = models.ForeignKey(Cancha, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cancha del Encuentro")
    fecha_y_hora_encuentro = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora Programada") 
    
    fase = models.CharField(max_length=50) # Ej: "Fecha 1", "Semifinal"
    goles_local = models.IntegerField(default=0)
    goles_visitante = models.IntegerField(default=0)
    penales_local = models.IntegerField(null=True, blank=True)
    penales_visitante = models.IntegerField(null=True, blank=True)
    goles_local = models.IntegerField(null=True, blank=True, verbose_name="Goles del Local")
    goles_visitante = models.IntegerField(null=True, blank=True, verbose_name="Goles del Visitante")
    penales_local = models.IntegerField(null=True, blank=True, verbose_name="Penales Local")
    penales_visitante = models.IntegerField(null=True, blank=True, verbose_name="Penales Visitante")
    jugado = models.BooleanField(default=False, verbose_name="Partido Finalizado")
    
    class Meta:
        verbose_name = "Partido"
        verbose_name_plural = "Partidos"

    def ganador(self):
        if not self.jugado: return None
        if self.penales_local is not None and self.penales_visitante is not None:
            return self.equipo_local if self.penales_local > self.penales_visitante else self.equipo_visitante
        if self.goles_local > self.goles_visitante: return self.equipo_local
        if self.goles_visitante > self.goles_local: return self.equipo_visitante
        return "Empate"

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fase}"