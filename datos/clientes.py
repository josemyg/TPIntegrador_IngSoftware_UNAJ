import random
from django.core.management.base import BaseCommand
from tuapp.models import Cliente
from datetime import datetime

# Listas de nombres y apellidos comunes sin acentos
nombres = [
    "Juan", "Pedro", "Maria", "Ana", "Carlos", "Lucas", 
    "Paula", "Sofía", "Diego", "Fernanda", "Jorge", "Rosa",
    "Eduardo", "Luis", "Gabriela", "Ricardo", "Mariana", "Pablo"
]

apellidos = [
    "Gonzalez", "Rodriguez", "Martinez", "Perez", "Lopez", "Gomez", 
    "Ramirez", "Sanchez", "Vargas", "Torres", "Mendez", "Hernandez",
    "Diaz", "Fernandez", "Gutierrez", "Moreno", "Castillo", "Jimenez"
]

# Listas de direcciones, localidades y provincias
calles = [
    "Calle 123", "Avenida 456", "Callejón 789", "Pasaje 101", 
    "Entre Ríos 200", "Buenos Aires 300", "Rosario 400", "Córdoba 500"
]

localidades = [
    "Buenos Aires", "Córdoba", "Rosario", "Mendoza", "Tucumán", 
    "Santa Fe", "La Plata", "Mar del Plata", "Salta", "San Miguel"
]

provincias = [
    "Buenos Aires", "Córdoba", "Rosario", "Mendoza", "Tucumán", 
    "Santa Fe", "La Plata", "Mar del Plata", "Salta", "San Miguel"
]

cp = [
    "1000", "1100", "1200", "1300", "1400", "1500", "1600", 
    "1700", "1800", "1900", "2000", "2100", "2200", "2300"
]

def generate_random_dni():
    """Genera un DNI aleatorio de 8 dígitos."""
    return str(random.randint(10000000, 99999999))

def generate_random_email(nombre, apellido):
    """Genera un correo electrónico aleatorio."""
    dominios = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"]
    return f"{nombre.lower()}.{apellido.lower()}@{random.choice(dominios)}"

def crear_clientes():
    for _ in range(100):
        # Generar datos aleatorios
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        direccion = random.choice(calles)
        localidad = random.choice(localidades)
        provincia = random.choice(provincias)
        pais = "Argentina"
        cpa = random.choice(cp)
        nacionalidad = "Argentina"
        telefono = f"{random.randint(11, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        email = generate_random_email(nombre, apellido)
        dni = generate_random_dni()
        
        # Crear y guardar un nuevo Cliente
        client = Cliente(
            nombre=nombre,
            apellido=apellido,
            direccion=direccion,
            localidad=localidad,
            provincia=provincia,
            pais=pais,
            cpa=cpa,
            nacionalidad=nacionalidad,
            telefono=telefono,
            email=email,
            dni=dni,
            fechaAlta=datetime.now().strftime("%d/%m/%Y"),
            estado="Activo",
            esSocio=random.choice([True, False])
        )
        client.save()

if __name__ == "__crear_clientes__":
    crear_clientes()


crear_clientes()