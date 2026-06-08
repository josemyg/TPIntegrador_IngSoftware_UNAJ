import random
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.conf import settings  # Import settings module
from django.contrib.auth.models import User

from gestion.models import Cliente, Profesor


def crear_profesor():
    """Crea un profesor con datos aleatorios."""
    nombres_profesores = ["Juan", "Pedro", "Carlos", "Diego", "Martin", "Lucas", "Facundo", "Agustín"]
    apellidos_profesores = ["Gonzalez", "Perez", "Martinez", "Lopez", "Rodriguez", "Sanchez", "Fernandez", "Gomez"]
    estados = Profesor.estados.keys()

    nombre = random.choice(nombres_profesores)
    apellido = random.choice(apellidos_profesores)
    email = f"{nombre.lower()}.{apellido.lower()}@example.com"  # Aseguramos correo sin acentos
    dni = ''.join(random.choices('0123456789', k=8))
    
    try:
        user = User.objects.create_user(nombre + " " + apellido, email, 'password')
        profesor = Profesor.objects.create(
            nombre=nombre,
            apellido=apellido,
            direccion="Calle Falsa 123",
            localidad="Buenos Aires",
            provincia="Buenos Aires",
            pais="Argentina",
            cpa="1000",
            nacionalidad="Argentina",
            telefono="011-5555-5555",
            email=email,
            dni=dni,
            user_django=user,
            usuario=usuario,
            titulo_habilitante="Profesor de algo",
            institucion_habilitante="Instituto de algo",
            estado=random.choice(estados),
        )
        return profesor
    except IntegrityError:
        print(f"Error: No se pudo crear profesor con email {email}.  Probablemente ya existe.")
        return None

def crear_cliente():
    """Crea un cliente con datos aleatorios."""
    nombres_clientes = ["Sofia", "Valentina", "Camila", "Isabella", "Mia", "Emma", "Olivia", "Lucia"]
    apellidos_clientes = ["Rodriguez", "Fernandez", "Gonzalez", "Perez", "Martinez", "Lopez", "Sanchez", "Gomez"]

    nombre = random.choice(nombres_clientes)
    apellido = random.choice(apellidos_clientes)
    email = f"{nombre.lower()}.{apellido.lower()}@example.com"  # Aseguramos correo sin acentos
    dni = ''.join(random.choices('0123456789', k=8))

    try:
        user = User.objects.create_user(nombre + " " + apellido, email, 'password')
        cliente = Cliente.objects.create(
            nombre=nombre,
            apellido=apellido,
            direccion="Calle Falsa 456",
            localidad="Cordoba",
            provincia="Cordoba",
            pais="Argentina",
            cpa="5000",
            nacionalidad="Argentina",
            telefono="0351-5555-5555",
            email=email,
            dni=dni,
            user_django=user,
            fechaAlta="2023-01-01",
            estado="activo",
            esSocio=False,
        )
        return cliente
    except IntegrityError:
        print(f"Error: No se pudo crear cliente con email {email}. Probablemente ya existe.")
        return None

def crear_muchos_profesores(cantidad):
    """Crea una cantidad especificada de profesores."""
    for _ in range(cantidad):
        profesor = crear_profesor()
        if profesor:
            print(f"Creado profesor: {profesor.nombre} {profesor.apellido}")
        else:
            print("No se pudo crear el profesor.")


def crear_muchos_clientes(cantidad):
    """Crea una cantidad especificada de clientes."""
    for _ in range(cantidad):
        cliente = crear_cliente()
        if cliente:
            print(f"Creado cliente: {cliente.nombre} {cliente.apellido}")
        else:
            print("No se pudo crear el cliente.")


# Para ejecutar en la shell de Django:
# from tu_app.scripts import crear_muchos_profesores, crear_muchos_clientes
# crear_muchos_profesores(50)
# crear_muchos_clientes(200)
