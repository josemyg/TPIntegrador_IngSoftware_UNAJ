import random
import string
from django.contrib.auth.models import User
from gestion.models import Profesor

def crear_profesores_argentinos():
    # Lista de nombres comunes en Argentina
    nombres = ['Maria', 'Juan', 'Ana', 'Pedro', 'Lucia', 'Jose', 'Camila', 'Matias', 'Valentina', 'Diego',
               'Florencia', 'Agustin', 'Mariana', 'Sebastian', 'Teresa', 'Andres', 'Rocio', 'Emanuel', 'Julieta',
               'Gonzalo', 'Paula', 'Santiago', 'Carolina', 'Luis', 'Marina', 'Jorge', 'Catalina', 'Nicolas',
               'Marta', 'Federico', 'Isabella', 'Oscar', 'Alejandra', 'Rodrigo', 'Elisa', 'Hernan', 'Clara',
               'Benjamin', 'Sofia', 'Eduardo', 'Melisa', 'Ricardo', 'Lucas', 'Ariadna', 'Enrique', 'Mia',
               'Rafael', 'Raquel', 'Fabian', 'Natalia', 'Horacio', 'Victoria', 'Gerardo', 'Elsa', 'Lautaro',
               'Paulina', 'Manuel', 'Estela', 'Arturo', 'Delfina', 'Raimundo', 'Carmen', 'Emilio', 'Nieves',
               'Pablo', 'Cecilia', 'Agustina', 'Bruno', 'Dolores', 'Cristian', 'Margarita', 'Alfredo', 'Lara',
               'Sergio', 'Gabriela', 'Hugo', 'Amelia', 'Luciano', 'Adrian', 'Rosa', 'Mariano', 'Ivana', 'Enzo']
    
    # Lista de apellidos comunes en Argentina
    apellidos = ['Gonzalez', 'Rodriguez', 'Martinez', 'Perez', 'Sanchez', 'Lopez', 'Fernandez', 'Gomez',
                 ' Ramirez', 'Diaz', 'Vazquez', 'Molina', 'Ojeda', 'Rios', 'Moreno', 'Peralta', 'Cortes',
                 'Ruiz', 'Vargas', 'Contreras', 'Perez', 'Ortega', 'Cabrera', 'Zarate', 'Sanchez', 'Marron',
                 'Crespo', 'Gimenez', 'Lopez', 'Rojas', 'Cid', 'Brizuela', 'Villafan', 'Pignata', 'Funes',
                 'Garcia', 'Saavedra', 'Carrizo', 'Llanos', 'Acosta', 'Torres', 'Caceres', 'Perez', 'Vidal',
                 'Ramon', 'Correa', 'Gimenez', 'Valenzuela', 'Bustos', 'Gomez', 'Villagra', 'Carrillo',
                 'Moreno', 'Quintana', 'Tirado', 'Cortez', 'Bautista', 'Serrano', 'Hernandez', 'Lopez',
                 'Gomez', 'Soto', 'Rojas', 'Caceres', 'Carrizo', 'Llanos', 'Acosta', 'Torres', 'Cacamo',
                 'Carrasco', 'Bustos', 'Gomez', 'Villafan', 'Pignata', 'Funes', 'Garcia', 'Saavedra',
                 'Carrizo', 'Llanos', 'Acosta', 'Torres', 'Caceres', 'Carrillo', 'Moreno', 'Quintana',
                 'Tirado', 'Cortez', 'Bautista', 'Serrano', 'Hernandez', 'Lopez', 'Gomez', 'Soto', 'Rojas',
                 'Caceres', 'Carrizo', 'Llanos', 'Acosta', 'Torres', 'Caceres', 'Carrillo', 'Moreno']    
    # Lista de títulos habilitantes
    titulos = ['Licenciado/a en Educación', 'Profesor/a de Educación Básica', 'Maestro/a en Pedagogía',
               'Educador/a en Formación', 'Título Superior en Enseñanza', 'Profesor/a de Nivel Medio',
               'Especialista en Docencia', 'Magister en Educación', 'Doctor/a en Ciencias de la Educación',
               'Técnico/a en Formación Docente']
    
    # Lista de instituciones habilitantes (instituciones educativas argentinas)
    instituciones = ['Ministerio de Educación de la Nación', 'Instituto Superior del Profesorado', 'Escuela Normal Superior',
                    'Universidad Nacional', 'Consejo General de Educación', 'Instituto Provincial de Enseñanza',
                    'Escuela de Formación Docente', 'Centro de Educación Integral', 'Instituto de Educación Superior',
                    'Escuela Técnica de Profesores', 'Colegio de Profesores de la Provincia']
    
    # Lista de ciudades en Argentina
    ciudades = ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'Santa Fe', 'Tucumán', 'La Plata', 'Mar del Plata',
                'Salta', 'San Miguel de Tucumán', 'San Juan', 'San Salvador de Jujuy', 'Resistencia', 'Corrientes',
                'Parana', 'Bahía Blanca', 'Villa Carlos Paz', 'Cañada Rosqueta', 'El Calafate', 'Bariloche',
                'Ushuaia', 'Puerto Iguazú', 'Córdoba', 'Tandil', 'Río Gallegos', 'Formosa', 'Posadas', 'Foz de Yacyretá']
    
    # Lista de provincias en Argentina
    provincias = ['Buenos Aires', 'Córdoba', 'Mendoza', 'Santa Fe', 'Tucumán', 'La Plata (provincia)', 'Salta',
                  'San Juan', 'Jujuy', 'Chaco', 'Corrientes', 'Misiones', 'Entre Ríos', 'Río Negro', 'Neuquén',
                  'Córdoba', 'Santiago del Estero', 'La Rioja', 'Catamarca', 'Tucumán', 'Chubut', 'Fuego',
                  'Tierra del Fuego', 'Buenos Aires', 'Córdoba', 'Mendoza', 'Santa Fe', 'Tucumán', 'La Plata']
    
    # País fijo como Argentina
    pais = 'Argentina'
    
    # Lista de sufijos para evitar duplicados en usernames
    sufijos = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    
    for i in range(100):
        # Generar nombre y apellido aleatorio
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        
        # Generar dirección aleatoria
        direccion = f"{random.randint(1, 1000)} {random.choice(['Calle', 'Avenida', 'Bulevar', 'Plaza', 'Diagonal'])} {random.choice(string.ascii_uppercase)}"
        
        # Generar localidad aleatoria
        localidad = random.choice(ciudades)
        
        # Generar provincia aleatoria
        provincia = random.choice(provincias)
        
        # País fijo
        pais_arg = pais
        
        # Generar código postal aleatorio (formato argentino: 5 o 6 dígitos)
        cpa = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        # Nacionalidad
        nacionalidad = pais_arg
        
        # Generar teléfono aleatorio (formato argentino: +54 11 1234-5678)
        telefono = f"+54 11 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        # Generar email aleatorio con dominio .ar
        email = f"{nombre.lower()}.{apellido.lower()}{random.choice(sufijos)}@unaj.edu.ar"
        
        # Generar DNI aleatorio (formato argentino: 8 dígitos)
        dni = f"{random.randint(10000000, 99999999)}"
        
        # Crear un usuario de Django con un username único
        username = f"{nombre.lower()}.{apellido.lower()}{random.choice(sufijos)}"
        password = 'f.123456'  # Contraseña fija para todos los usuarios
        
        # Crear el usuario
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        # Crear el profesor
        profesor = Profesor(
            nombre=nombre,
            apellido=apellido,
            direccion=direccion,
            localidad=localidad,
            provincia=provincia,
            pais=pais_arg,
            cpa=cpa,
            nacionalidad=nacionalidad,
            telefono=telefono,
            email=email,
            dni=dni,
            user_django=user,
            
            # Campos específicos del Profesor
            titulo_habilitante=random.choice(titulos),
            institucion_habilitante=random.choice(instituciones),
            estado=random.choice(['activo', 'inactivo', 'baja', 'en_validacion'])
        )
        
        profesor.save()
        print(f"Profesor {nombre} {apellido} creado correctamente.")

# Llama a la función
crear_profesores_argentinos()