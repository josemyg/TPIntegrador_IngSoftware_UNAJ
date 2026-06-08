import random
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from clases_y_entrenamientos.models import Clase, Entrenamiento
from gestion.models import Profesor, Cliente

def crear_clases_entrenamientos():
    # Obtener todos los profesores existentes
    profesores = list(Profesor.objects.all())
    
    # Obtener todos los clientes (alumnos) existentes
    alumnos = list(Cliente.objects.all())
    
    # Crear 100 clases
    for _ in range(100):
        # Seleccionar aleatoriamente un profesor
        profesor = random.choice(profesores)
        
        # Determinar la cantidad de alumnos para esta clase (máximo 10)
        cupo_maximo = 10
        cantidad_alumnos = random.randint(1, min(cupo_maximo, len(alumnos)))
        
        # Seleccionar aleatoriamente alumnos sin repetir
        alumnos_clase = random.sample(alumnos, cantidad_alumnos)
        
        # Crear la clase
        horario = datetime.now() + timedelta(days=random.randint(1, 30))
        clase = Clase.objects.create(
            nombre=f"Clase {random.randint(1, 1000)}",
            horario=horario,
            profesor=profesor,
            cupo_maximo=cupo_maximo
        )
        
        # Asignar alumnos a la clase
        clase.alumnos.set(alumnos_clase)
    
    # Crear 100 entrenamientos
    for _ in range(100):
        # Seleccionar aleatoriamente un profesor
        profesor = random.choice(profesores)
        
        # Determinar la cantidad de alumnos para este entrenamiento (máximo 10)
        cupo_maximo = 10
        cantidad_alumnos = random.randint(1, min(cupo_maximo, len(alumnos)))
        
        # Seleccionar aleatoriamente alumnos sin repetir
        alumnos_entrenamiento = random.sample(alumnos, cantidad_alumnos)
        
        # Crear el entrenamiento
        horario = datetime.now() + timedelta(days=random.randint(1, 30))
        entrenamiento = Entrenamiento.objects.create(
            nombre=f"Entrenamiento {random.randint(1, 1000)}",
            horario=horario,
            entrenador=profesor,
            cupo_maximo=cupo_maximo
        )
        
        # Asignar alumnos al entrenamiento
        entrenamiento.alumnos.set(alumnos_entrenamiento)
    
    print("Se han creado 100 clases y 100 entrenamientos con profesores y alumnos existentes.")

if __name__ == "__crear_clases_entrenamientos__":
    crear_clases_entrenamientos()


#crear_clases_entrenamientos()