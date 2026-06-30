from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from datetime import datetime, timedelta,time
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from gestion.models import Cliente, Profesor
from gestion.forms import ProfesorForm, ProfesorSinValidarForm, ClienteForm
from reservas.models import Reserva
from pagos.models import Pago,TipoPago
from pagos.forms import PagoForm
from canchas.models import Cancha
from clases_y_entrenamientos.models import Clase, Entrenamiento, AsistenciaClase, AsistenciaEntrenamiento
from competiciones.models import Equipo, Competicion, Liga, Torneo
from vistas.forms import ClientePerfilForm
from .forms import ReservaForm


def get_cliente_por_usuario(user):
    try:
        return Cliente.objects.get(user_django=user)
    except Cliente.DoesNotExist:
        return None

class ClientePerfilUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClientePerfilForm
    template_name = 'vistas/cliente_perfil_form.html'

    def get_object(self, queryset=None):
        return get_cliente_por_usuario(self.request.user)

    def get_success_url(self):
        return reverse_lazy('vistas:dashboard_bienvenida')

@login_required
def dashboard_cliente(request):
    cliente = get_cliente_por_usuario(request.user)
    print(cliente)
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
        print(es_cliente)
    except:
        pass
    if not es_cliente:
        return redirect('/administracion')
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



@login_required
def mis_actividades(request):
    cliente = get_cliente_por_usuario(request.user)
    es_cliente = cliente.verificarCliente()
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
    except:
        pass
    if not es_cliente:
        return redirect('login')
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


@login_required
def mis_reservas(request):
    cliente = get_cliente_por_usuario(request.user)
    es_cliente = cliente.verificarCliente()
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
    except:
        pass
    if not es_cliente:
        return redirect('login')
    reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    return render(request, 'vistas/mis_reservas.html', {'reservas': reservas})



@login_required
def mis_reservas_crear(request):
    cliente = get_cliente_por_usuario(request.user)
    es_cliente = cliente.verificarCliente()
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
    except:
        pass
    if not es_cliente:
        return redirect('login')  
    if request.method == 'POST':
        cancha_id = request.POST.get('cancha')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        
        if cancha_id and fecha and hora_inicio:
            cancha = get_object_or_404(Cancha, id=cancha_id)
            hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M')
            hora_fin_dt = hora_inicio_dt + timedelta(minutes=60)
            
           
            reserva = Reserva.objects.create(
                cancha=cancha,
                fecha=fecha,
                hora_inicio=hora_inicio_dt.time(),
                hora_fin=hora_fin_dt.time(),
                cliente=cliente,
                estado='PENDIENTE',
                precio_final=cancha.tipo.precio_hora
            )
            return redirect('pago_create_reserva', reserva_id=reserva.id)
    canchas = Cancha.objects.filter(estado='DISPONIBLE')
    reservas = None
    horarios_libres = []
    
    hoy_dt = datetime.today()
    max_fecha_dt = hoy_dt + timedelta(days=7)
    hoy_str = hoy_dt.strftime('%Y-%m-%d')
    max_fecha_str = max_fecha_dt.strftime('%Y-%m-%d')
    
    fecha = request.GET.get('fecha')
    cancha_id = request.GET.get('cancha')
    
    if fecha:
        try:
            fecha_seleccionada = datetime.strptime(fecha, '%Y-%m-%d')
            if fecha_seleccionada.date() < hoy_dt.date() or fecha_seleccionada.date() > max_fecha_dt.date():
                fecha = hoy_str
        except ValueError:
            fecha = hoy_str
            
    if fecha and cancha_id:
        reservas = Reserva.objects.filter(
            fecha=fecha, cancha_id=cancha_id
        ).exclude(estado__startswith='CANCELADA').order_by('hora_inicio')
        
        intervalos_ocupados = [(r.hora_inicio, r.hora_fin) for r in reservas]
        
        hora_actual = datetime.combine(datetime.today(), time(8, 0))
        hora_cierre = datetime.combine(datetime.today(), time(23, 0))
        
        while hora_actual < hora_cierre:
            inicio = hora_actual.time()
            fin = (hora_actual + timedelta(minutes=60)).time()
            es_pasado = False
            if fecha == hoy_str:
                if inicio <= datetime.now().time():
                    es_pasado = True
            ocupado = any(
                hora_inicio_res < fin and hora_fin_res > inicio
                for hora_inicio_res, hora_fin_res in intervalos_ocupados
            )
            
            if not ocupado and not es_pasado:
                horarios_libres.append({
                    'hora_inicio': inicio.strftime('%H:%M'),
                    'texto': f"{inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')}"
                })
            hora_actual += timedelta(minutes=60)
    fecha_obj = None
    if fecha:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')

    return render(request, 'vistas/mis_reservas_form.html', {
        'canchas': canchas,
        'reservas': reservas,
        'fecha': fecha,
        'fecha_obj': fecha_obj,
        'cancha_id': cancha_id,
        'horarios_libres': horarios_libres,
        'hoy': hoy_str,
        'max_fecha': max_fecha_str,
    })

@login_required
def mis_reservas_cancelar(request, reserva_id):
    cliente = get_cliente_por_usuario(request.user)
    es_cliente = cliente.verificarCliente()
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
    except:
        pass
    if not es_cliente:
        return redirect('login')
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=cliente)
    ahora = datetime.now()
    fecha_reserva = datetime.combine(reserva.fecha, reserva.hora_inicio)
    diferencia = fecha_reserva - ahora

    if diferencia < timedelta(hours=6):
        reserva.estado = 'CANCELADA CON CARGO'
        messages.error(request, 'La reserva fue cancelada fuera del plazo de 6hs permitido. Se aplicó un cargo a tu cuenta.')
    else:
        reserva.estado = 'CANCELADA CON REEMBOLSO'
        messages.success(request, 'La reserva fue cancelada correctamente y a tiempo. Se procesará el reembolso o anulación del pago.')

    reserva.save()
    return redirect('vistas:mis_reservas')

@login_required
def mis_pagos(request):
    cliente = get_cliente_por_usuario(request.user)
    es_cliente = cliente.verificarCliente()
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
    except:
        pass
    if not es_cliente:
        return redirect('login')
    
   
    equipos_cliente = Equipo.objects.filter(clientes=cliente)

    pagos = Pago.objects.filter(
        Q(reserva__cliente=cliente) | Q(equipo__in=equipos_cliente)
    ).order_by('-fecha')
    
    total_adeudado = sum(p.monto_final for p in pagos if p.estado == 'PENDIENTE')
    return render(request, 'vistas/mis_pagos.html', {'pagos': pagos, 'total_adeudado': total_adeudado})

@login_required
def mis_inscripciones(request):
    cliente = get_cliente_por_usuario(request.user)
    es_cliente = cliente.verificarCliente()
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
    except:
        pass
    if not es_cliente:
        return redirect('login')
        
    equipos_cliente = Equipo.objects.filter(clientes=cliente)
    
    pagos = Pago.objects.filter(estado='PAGADO', competicion__isnull=False, equipo__in=equipos_cliente)
    
    pagos_lista = [f"{p.equipo.id}-{p.competicion.id}" for p in pagos]
    
    return render(request, 'vistas/mis_inscripciones.html', {
        'equipos': equipos_cliente, 
        'pagos_lista': pagos_lista
    })

@login_required
def pagar_inscripcion_cliente(request, competicion_id, equipo_id):
    competicion = get_object_or_404(Competicion, id=competicion_id)
    equipo = get_object_or_404(Equipo, id=equipo_id)

    if Pago.objects.filter(equipo=equipo, competicion=competicion, estado='PAGADO').exists():
        messages.info(request, "Esta inscripción ya se encuentra abonada.")
        return redirect('vistas:mis_pagos')

    es_liga = Liga.objects.filter(id=competicion.id).exists()
    origen = 'inscripcion_liga' if es_liga else 'inscripcion_torneo'
    qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=123"
    monto_oficial = 25000.00 

    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.equipo = equipo
            pago.competicion = competicion
            pago.origen_pago = origen
            pago.estado = 'PENDIENTE'
            
            pago.monto = pago.calcular_monto_con_descuento(monto_oficial)
            pago.save()
            competicion.equipos.add(equipo)

            messages.success(request, f"¡Pago exitoso! El equipo {equipo.nombre} completó su inscripción.")
            return redirect('vistas:mis_pagos')
    else:
        form = PagoForm(initial={
            'monto': monto_oficial,
            'origen_pago': origen,
        })

    return render(request, 'pagos/pago_form.html', {'form': form, 'competicion_actual': competicion, 'equipo_actual': equipo, 'es_cliente': not request.user.is_staff, 'qr_code': qr_code})

@login_required
def cancelar_pago_y_reserva(request, reserva_id):
    cliente = get_cliente_por_usuario(request.user)
    es_cliente = cliente.verificarCliente()
    es_cliente = False
    try:
        es_cliente = cliente.verificarCliente()
    except:
        pass
    if not es_cliente:
        return redirect('login')
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=cliente)
    Pago.objects.filter(reserva=reserva).delete()
    reserva.delete()
    messages.info(request, "Reserva cancelada")
    return redirect('vistas:mis_reservas')
