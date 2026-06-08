#from .clientes import crear_clientes
from .profesores import crear_profesores_argentinos
#from .profesores_y_clientes import crear_muchos_profesores, crear_muchos_clientes
from .canchas import create_stadiums
from .clases_y_entrenamientos import crear_clases_entrenamientos
from .equipos import create_teams

#from gestion.models import Cliente, Profesor
from canchas.models import Cancha, TipoCancha
from clases_y_entrenamientos.models import Clase, Entrenamiento
from competiciones.models import Equipo



def carga_masiva():
    crear_clientes()
    crear_muchos_clientes(200)
    crear_muchos_profesores(50)
    crear_profesores_argentinos()
    create_stadiums()
    crear_clases_entrenamientos()
    create_teams()

