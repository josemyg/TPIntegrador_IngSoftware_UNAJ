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
from django.contrib import messages
from .forms import ReservaForm

class ClientePerfilUpdateView(UpdateView):
    model = Cliente
    form_class = ClientePerfilForm
    template_name = 'vistas/cliente_perfil_form.html'

    def get_success_url(self):
        return reverse_lazy('vistas:dashboard_cliente')

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



def mis_actividades(request):
    cliente = request.user  # asumiendo que request.user es el cliente
    clases_futuras = cliente.clases.filter(estado__in=['programada', 'en_curso']).order_by('horario')
    entrenamientos_futuros = cliente.entrenamientos.filter(estado__in=['programado', 'en_curso']).order_by('horario')
    clases_pasadas = cliente.clases.filter(estado__in=['finalizada', 'cancelada']).order_by('-horario')
    entrenamientos_pasados = cliente.entrenamientos.filter(estado__in=['finalizado', 'cancelado']).order_by('-horario')
    asistencias_clase = AsistenciaClase.objects.filter(alumno=cliente).select_related('clase')
    asistencias_entrenamiento = AsistenciaEntrenamiento.objects.filter(alumno=cliente).select_related('entrenamiento')
    context = {
        'clases_futuras': clases_futuras,
        'entrenamientos_futuros': entrenamientos_futuros,
        'clases_pasadas': clases_pasadas,
        'entrenamientos_pasados': entrenamientos_pasados,
        'asistencias_clase': asistencias_clase,
        'asistencias_entrenamiento': asistencias_entrenamiento,
    }
    return render(request, 'vistas/mis_actividades.html', context)


def mis_reservas(request):
    cliente = request.user
    reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    return render(request, 'vistas/mis_reservas.html', {'reservas': reservas})


def mis_reservas_crear(request):
    cliente = request.user
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = cliente
            reserva.save()
            messages.success(request, "Reserva creada exitosamente.")
            return redirect('vistas:mis_reservas')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos.")
    else:
        form = ReservaForm()
    return render(request, 'vistas/mis_reservas_form.html', {'form': form})


def mis_pagos(request):
    cliente = request.user
    pagos = Pago.objects.filter(reserva__cliente=cliente).order_by('-fecha')
    total_adeudado = sum(p.monto_final for p in pagos if p.estado == 'PENDIENTE')
    return render(request, 'vistas/mis_pagos.html', {'pagos': pagos, 'total_adeudado': total_adeudado})


def mis_inscripciones(request):
    cliente = request.user
    equipos_cliente = Equipo.objects.filter(clientes=cliente)
    competiciones = Competicion.objects.filter(equipos__in=equipos_cliente).distinct().order_by('-id')
    return render(request, 'vistas/mis_inscripciones.html', {'equipos': equipos_cliente, 'competiciones': competiciones})