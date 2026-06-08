import random
from django.core.management.base import BaseCommand
from canchas.models import TipoCancha, Cancha

def create_stadiums():
    # Lista de nombres de estadios argentinos y conocidos del mundo
    stadium_names = [
        "Estadio River Plate", "Estadio Boca Juniors", "Estadio Maracaná",
        "Cancha N° 1 Techada", "Cancha N° 2 Techada", "Cancha N° 3 Techada",
        "Cancha N° 4 Techada", "Cancha N° 5 Techada", "Cancha N° 6 Techada",
        "Cancha N° 7 Techada", "Cancha N° 8 Techada", "Cancha N° 9 Techada",
        "Cancha N° 10 Techada", "Cancha N° 11 Techada", "Cancha N° 12 Techada",
        "Cancha N° 13 Techada", "Cancha N° 14 Techada", "Cancha N° 15 Techada",
        "Cancha N° 16 Techada", "Cancha N° 17 Techada", "Cancha N° 18 Techada",
        "Cancha N° 19 Techada", "Cancha N° 20 Techada", "Cancha N° 21 Techada",
        "Cancha N° 22 Techada", "Cancha N° 23 Techada", "Cancha N° 24 Techada",
        "Cancha N° 25 Techada", "Cancha N° 26 Techada", "Cancha N° 27 Techada",
        "Cancha N° 28 Techada", "Cancha N° 29 Techada", "Cancha N° 30 Techada",
        "Cancha N° 31 Techada", "Cancha N° 32 Techada", "Cancha N° 33 Techada",
        "Cancha N° 34 Techada", "Cancha N° 35 Techada", "Cancha N° 36 Techada",
        "Cancha N° 37 Techada", "Cancha N° 38 Techada", "Cancha N° 39 Techada",
        "Cancha N° 40 Techada", "Cancha N° 41 Techada", "Cancha N° 42 Techada",
        "Cancha N° 43 Techada", "Cancha N° 44 Techada", "Cancha N° 45 Techada",
        "Cancha N° 46 Techada", "Cancha N° 47 Techada", "Cancha N° 48 Techada",
        "Cancha N° 49 Techada", "Cancha N° 50 Techada", "Cancha N° 51 Techada",
        "Cancha N° 52 Techada", "Cancha N° 53 Techada", "Cancha N° 54 Techada",
        "Cancha N° 55 Techada", "Cancha N° 56 Techada", "Cancha N° 57 Techada",
        "Cancha N° 58 Techada", "Cancha N° 59 Techada", "Cancha N° 60 Techada",
    ]

    # Crear 20 tipos de cancha
    for _ in range(20):
        tipo = TipoCancha(
            nombreTipo=f"Tipo {_ + 1}",
            capacidad=random.randint(10, 50),
            superficie=random.choice(['cesped_natural', 'sintetico']),
            precio_hora=random.uniform(50, 200),
            estado='activo',
            max_horas=random.choice([2, 3])
        )
        tipo.save()

    # Crear 60 canchas
    for i in range(60):
        cancha = Cancha(
            nombre=stadium_names[i],
            tipo=TipoCancha.objects.order_by('?').first(),  # Selecciona un tipo al azar
            estado='activo'
        )
        cancha.save()

    print("Se han creado 20 tipos de cancha y 60 canchas exitosamente.")

if __name__ == "__main__":
    create_stadiums()