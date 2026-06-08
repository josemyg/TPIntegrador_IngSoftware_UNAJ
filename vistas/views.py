from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
from django.contrib.auth.models import User


from gestion.models import Cliente, Profesor
from gestion.forms import ProfesorForm, ProfesorSinValidarForm, ClienteForm
from reservas.models import Reserva
from pagos.models import Pago
from canchas.models import Cancha
from clases_y_entrenamientos.models import Clase, Entrenamiento, AsistenciaClase, AsistenciaEntrenamiento
from competiciones.models import Equipo, Competicion, Liga, Torneo
from vistas.forms import ClientePerfilForm

# Create your views here.
class ClientePerfilUpdateView(UpdateView):
    model = Cliente
    form_class = ClientePerfilForm
    template_name = 'vistas/cliente_perfil_form.html'

    def get_success_url(self):
        return reverse_lazy('vistas:dashboard_cliente', kwargs={'pk': self.object.pk})

def dashboard_cliente(request):
    cliente = request.user
    # Clases
    try:
        clases = cliente.clases.all()
        clases_activas = clases.filter(estado__in=['programada', 'en_curso'])
        proxima_clase = clases_activas.order_by('horario').first()
    except:
        clase = None
        clases_activas = None
        proxima_clase = None
    # Entrenamientos
    try:
        entrenamientos = cliente.entrenamientos.all()
        entrenamientos_activos = entrenamientos.filter(
            estado__in=['programado', 'en_curso'])
        proximo_entrenamiento = entrenamientos_activos.order_by('horario').first()
    except:
        entrenamientos = None
        entrenamientos_activos = None
        proximo_entrenamiento = None

    # Asistencia a clases
    try:
        asistencias_clase = AsistenciaClase.objects.filter(alumno=cliente)
        total_clases = asistencias_clase.count()
        presentes_clases = asistencias_clase.filter(asistencia=True).count()
        porcentaje_clases = round(
            presentes_clases / total_clases * 100) if total_clases > 0 else 0
    except:
        asistencias_clase = None
        total_clases = None
        presentes_clases = None
        porcentaje_clases = None
    # Asistencia  a entrenamientos
    try:
        asistencias_entrenamiento = AsistenciaEntrenamiento.objects.filter(
            alumno=cliente)
        total_entrenamientos = asistencias_entrenamiento.count()
        presentes_entrenamientos = asistencias_entrenamiento.filter(asistencia=True).count()
        porcentaje_entrenamientos = round(
            presentes_entrenamientos / total_entrenamientos * 100) if total_entrenamientos > 0 else 0
    except:
        asistencias_entrenamiento = None
        total_entrenamientos = None
        presentes_entrenamientos = None
        porcentaje_entrenamientos = None

    # Reservas
    try:
        reservas = Reserva.objects.filter(
            cliente=cliente).order_by('-fecha_creacion')
    except:
        reservas = None

    # Pagos
    try:
        pagos = Pago.objects.filter(reserva__cliente=cliente).order_by('-fecha')
    except:
        pagos = None

        #Equipos
    try:
        equipos_cliente = Equipo.objects.filter(clientes=cliente)
    except:
        equipos_cliente = None

        #Ligas
    try:
        ligas = Liga.objects.filter(equipos__in=equipos_cliente).exclude(estado='Finalizada').distinct()
    except:
        ligas = None

        #Torneos
    try:
        torneos = Torneo.objects.filter(equipos__in=equipos_cliente).exclude(estado='Finalizada').distinct()
    except:
        torneos = None

    
    return render(request, 'vistas/dashboard_cliente.html', {
        'cliente': cliente,
        'clases_activas': clases_activas,
        'proxima_clase': proxima_clase,
        'entrenamientos_activos': entrenamientos_activos,
        'proximo_entrenamiento': proximo_entrenamiento,
        'porcentaje_clases': porcentaje_clases,
        'presentes_clases': presentes_clases,
        'total_clases': total_clases,
        'porcentaje_entrenamientos': porcentaje_entrenamientos,
        'presentes_entrenamientos': presentes_entrenamientos,
        'total_entrenamientos': total_entrenamientos,
        'reservas': reservas,
        'pagos': pagos,
        'equipos': equipos_cliente,
        'ligas': ligas,
        'torneos': torneos,
    })