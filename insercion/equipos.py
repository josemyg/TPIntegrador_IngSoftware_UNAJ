import random
from django.core.management.base import BaseCommand
from gestion.models import Profesor, Cliente
from competiciones.models import Equipo

# Lista inicial de nombres de clubes argentinos
club_base = [
    'Boca Juniors',
    'River Plate',
    'Argentinos Juniors',
    'Independiente',
    'Rosario Central',
    'San Lorenzo',
    'Racing Club',
    'Talleres',
    'Club Atlético',
    'Huracán',
    'Sarmiento',
    'Mandiyú',
    'Almagro',
    'Platense',
    'Comunicacional',
    'Instituto',
    'Nacional',
    'Olimpo',
    'Quilmes',
    'Roma',
    'Santo Domingo',
    'Sportivo Italiano',
    'Tiro Federal',
    'Unión',
    'Vélez Sársfield',
    'Barracas Central',
    'Boca Unidos',
    'Deportivo Moron',
    'Estudiantes',
    'Fénix',
    'General Lamadrid',
    'Ituzaingó',
    'Luján',
    'Mallorca',
    'Náutico',
    'Pellegrini',
    'Real Madrid',
    'Rosario FC',
    'Santos Laguna',
    'Temperley',
    'UAI Urquita',
    'Unión de Santa Fe',
    'Villa Dalmine',
    'Zárate'
]

def create_teams():
    # Asegúrese de que hay profesores y clientes en la base de datos
    if not Profesor.objects.exists() or not Cliente.objects.exists():
        print("No hay profesores o clientes en la base de datos.")
        return
    
    # Obtener listas de profesores y clientes
    proffesors = list(Profesor.objects.all())
    clients = list(Cliente.objects.all())
    
    # Generar 50 nombres únicos de equipos
    used_names = set()
    for _ in range(50):
        # Seleccionar aleatoriamente dos palabras de la base
        prefix = random.choice(club_base)
        suffix = random.choice(['Club', 'Instituto', 'Sociedad', 'Asociación'])
        name = f"{prefix} {suffix}"
        
        # Asegurarse de que el nombre no haya sido utilizado antes
        while name in used_names:
            suffix = random.choice(['Club', 'Instituto', 'Sociedad', 'Asociación'])
            name = f"{prefix} {suffix}"
        
        used_names.add(name)
        
        # Seleccionar profesor y clientes
        profesor = random.choice(proffesors)
        num_clients = random.randint(5, 10)
        selected_clients = random.sample(clients, num_clients) if len(clients) >= num_clients else clients
        
        # Crear el equipo
        team = Equipo.objects.create(
            nombre=name,
            profesor=profesor
        )
        
        # Extraer los IDs de los clientes seleccionados
        client_ids = [cliente.id for cliente in selected_clients]
        
        # Agregar los clientes al equipo
        team.clientes.add(*client_ids)
        print(f"Equipo creado: {name} con profesor {profesor} y {len(selected_clients)} alumnos.")

# Ejecutar la función
#create_teams()
