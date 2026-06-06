import os
from django.core.management.base import BaseCommand
from django.db import transaction
from tu_app.models import TipoCancha, Cancha
import random

def crear_tipos_cancha():
    tipos = [
        {
            'nombre': f'Tipo %02d' % i,
            'capacidad': random.randint(10, 50),
            'superficie': 'cesped_natural' if i % 2 == 0 else 'sintetico',
            'precio_hora': round(random.uniform(10, 100), 2),
            'estado': 'activo'
        }
        for i in range(1, 16)
    ]
    
    with transaction.atomic():
        for tipo in tipos:
            TipoCancha.objects.create(**tipo)
    
    print(f"Se crearon {len(tipos)} tipos de cancha exitosamente.")

def crear_canchas():
    # Primero creamos 15 tipos de cancha
    crear_tipos_cancha()
    
    # Creamos 40 canchas
    canchas = []
    for i in range(1, 41):
        tipo = random.choice(TipoCancha.objects.all())
        canchas.append(
            Cancha(
                nombre=f'Cancha %02d' % i,
                tipo=tipo,
                estado=random.choice(['activo', 'mantenimiento', 'inactivo'])
            )
        )
    
    with transaction.atomic():
        Cancha.objects.bulk_create(canchas)
    
    print(f"Se crearon {len(canchas)} canchas exitosamente.")

class Command(BaseCommand):
    help = 'Crea 15 tipos de cancha y 40 canchas'
    
    def handle(self, *args, **options):
        crear_canchas()

crear_canchas()