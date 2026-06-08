import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

# Asegúrate de import os
import random
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from app.models import Equipo, Competicion, Liga, Torneo, Partido, Profesor, Cliente, Cancha

def crearEquiposYPartidos():
    """
    Crea 50 equipos y 200 partidos con datos aleatorios.
    """
    nombres_equipos = [
        'River Plate', 'Boca Juniors', 'Rosario Central', 'Racing Club',
        'Argentinos Juniors', 'San Lorenzo', 'Independiente', 'Vélez Sársfield',
        'Talleres de Córdoba', 'Deportivo Cali', 'Club Atletico', 'Huracán',
        'Defensa y Justicia', 'Estudiantes de La Plata', 'UAI Urquía', 'Colón',
        'Newell`s Old Boys', 'Godoy Cruz', 'Almagro', 'Sarmiento', 'Mitre',
        'Gimnasia y Esgrima', 'Ferro Carril Oeste', 'Platense', 'Barracas Central',
        'Argentino Juniors', 'Chaco For Ever', 'Cerro Porteño', 'Libertad',
        'Olimpia', 'Nacional', 'Inter de Porto Alegre', 'Gremio', 'Flamengo',
        'Flamengo', 'Vasco da Gama', 'Santos', 'Corinthians', 'Palmeiras',
        'Sao Paulo', 'Atletico Mineiro', 'Belo Horizonte', 'Cruzeiro',
        'Botafogo', 'Atletico Paranaense', 'Coritiba', 'Paranaense',
        'Curitiba', 'Brasilia', 'Guarani', 'Portuguesa', 'Ponte Preta',
        'Vasco da Gama', 'Tijuana', 'Monterrey', 'Chivas', 'Pumas', 'Toluca'
    ]

    @transaction.atomic
    def crearEquipos():
        # Crear 50 equipos
        for i in range(50):
            nombre = random.choice(nombres_equipos)
            profesor = random.choice(Profesor.objects.all())
            # Crear un equipo
            equipo = Equipo.objects.create(
                nombre=nombre,
                profesor=profesor
            )
            # Agregar 3-5 clientes aleatorios
            clientes = random.sample(list(Cliente.objects.all()), random.randint(3,5))
            equipo.clientes.add(*clientes)
            print(f'Creando equipo: {nombre}')

    def crearCompeticiones():
        ligas = []
        torneos = []
        for _ in range(5):
            # Crear Liga
            liga = Liga.objects.create(
                nombre=f'Liga {_}',
                puntos_victoria=3,
                puntos_empate=1
            )
            ligas.append(liga)
            # Crear Torneo
            torneo = Torneo.objects.create(
                nombre=f'Torneo {_}',
                es_ida_y_vuelta=random.choice([True, False])
            )
            torneos.append(torneo)

    def crearPartidos():
        # Crear 200 partidos
        for _ in range(200):
            # Seleccionar aleatoriamente una competición
            competicion = random.choice(ligas + torneos)
            # Seleccionar dos equipos
            equipos = list(Equipo.objects.all())
            equipo_local = random.choice(equipos)
            equipos.remove(equipo_local)
            equipo_visitante = random.choice(equipos)
            # Seleccionar cancha
            cancha = random.choice(Cancha.objects.all())
            # Crear fecha y hora aleatoria
            fecha_hora = timezone.now() + timedelta(days=random.randint(1, 30))
            # Crear partido
            partido = Partido.objects.create(
                competicion=competicion,
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                cancha=cancha,
                fecha_hora=fecha_hora,
                fase=f'Fase {_ % 10}'
            )
            # Asignar goles aleatorios
            goles_local = random.randint(0, 5)
            goles_visitante = random.randint(0, 5)
            partido.goles_local = goles_local
            partido.goles_visitante = goles_visitante
            partido.save()
            print(f'Creando partido: {equipo_local} vs {equipo_visitante}')

    print("Iniciando creación de equipos...")
    crearEquipos()
    print("\nCreando competiciones...")
    crearCompeticiones()
    print("\nCreando partidos...")
    crearPartidos()
    print("\n¡Se crearon todos los equipos y partidos exitosamente!")

if __name__ == "__main__":
    crearEquiposYPartidos()
    
    #importar tus modelos
from app.models import Equipo, Competicion, Liga, Torneo, Partido, Profesor, Cliente, Cancha

class Command(BaseCommand):
    help = 'Crea 50 equipos y 200 partidos'

    @transaction.atomic
    def handle(self, *args, **options):
        # Lista de nombres de clubes de fútbol argentinos
        nombres_equipos = [
            'River Plate', 'Boca Juniors', 'Rosario Central', 'Racing Club',
            'Argentinos Juniors', 'San Lorenzo', 'Independiente', 'Vélez Sársfield',
            'Talleres de Córdoba', 'Deportivo Cali', 'Club Atletico', 'Huracán',
            'Defensa y Justicia', 'Estudiantes de La Plata', 'UAI Urquía', 'Colón',
            'Newell`s Old Boys', 'Godoy Cruz', 'Almagro', 'Sarmiento', 'Mitre',
            'Gimnasia y Esgrima', 'Ferro Carril Oeste', 'Platense', 'Barracas Central',
            'Argentino Juniors', 'Chaco For Ever', 'Cerro Porteño', 'Libertad',
            'Olimpia', 'Nacional', 'Inter de Porto Alegre', 'Gremio', 'Flamengo',
            'Flamengo', 'Vasco da Gama', 'Santos', 'Corinthians', 'Palmeiras',
            'Sao Paulo', 'Atletico Mineiro', 'Belo Horizonte', 'Cruzeiro',
            'Botafogo', 'Atletico Paranaense', 'Coritiba', 'Paranaense',
            'Curitiba', 'Brasilia', 'Guarani', 'Portuguesa', 'Ponte Preta',
            'Vasco da Gama', 'Tijuana', 'Monterrey', 'Chivas', 'Pumas', 'Toluca'
        ]

        # Crear 50 equipos
        for i in range(50):
            nombre = random.choice(nombres_equipos)
            profesor = random.choice(Profesor.objects.all())
            # Crear un equipo
            equipo = Equipo.objects.create(
                nombre=nombre,
                profesor=profesor
            )
            # Agregar 3-5 clientes aleatorios
            clientes = random.sample(list(Cliente.objects.all()), random.randint(3,5))
            equipo.clientes.add(*clientes)
            self.stdout.write(f'Creando equipo: {nombre}')

        # Crear competiciones
        ligas = []
        torneos = []
        for _ in range(5):
            # Crear Liga
            liga = Liga.objects.create(
                nombre=f'Liga {_}',
                puntos_victoria=3,
                puntos_empate=1
            )
            ligas.append(liga)
            # Crear Torneo
            torneo = Torneo.objects.create(
                nombre=f'Torneo {_}',
                es_ida_y_vuelta=random.choice([True, False])
            )
            torneos.append(torneo)

        # Crear 200 partidos
        for _ in range(200):
            # Seleccionar aleatoriamente una competición
            competicion = random.choice(ligas + torneos)
            # Seleccionar dos equipos
            equipos = list(Equipo.objects.all())
            equipo_local = random.choice(equipos)
            equipos.remove(equipo_local)
            equipo_visitante = random.choice(equipos)
            # Seleccionar cancha
            cancha = random.choice(Cancha.objects.all())
            # Crear fecha y hora aleatoria
            fecha_hora = timezone.now() + timedelta(days=random.randint(1, 30))
            # Crear partido
            partido = Partido.objects.create(
                competicion=competicion,
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                cancha=cancha,
                fecha_hora=fecha_hora,
                fase=f'Fase {_ % 10}'
            )
            # Asignar goles aleatorios
            goles_local = random.randint(0, 5)
            goles_visitante = random.randint(0, 5)
            partido.goles_local = goles_local
            partido.goles_visitante = goles_visitante
            partido.save()
            self.stdout.write(f'Creando partido: {equipo_local} vs {equipo_visitante}')

        self.stdout.write(self.style.SUCCESS('¡Se crearon todos los equipos y partidos exitosamente!'))

