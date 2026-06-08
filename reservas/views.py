from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva
from canchas.models import Cancha, TipoCancha
from .forms import ReservaForm
from django.db.models import Q
from datetime import datetime, timedelta,time
from django.contrib import messages
from gestion.models import Usuario
from django.contrib.auth.decorators import permission_required



@permission_required("reservas.view_reserva")
def gestion_reservas(request):

    if request.method == 'POST': # Si el método de la solicitud es POST, significa que se está enviando un formulario para crear una nueva reserva.

        form = ReservaForm(request.POST) # Crea una instancia del formulario ReservaForm con los datos enviados en la solicitud POST.

        if form.is_valid():

            reserva = form.save() 

            return redirect(
                'pago_create_reserva',
                reserva_id=reserva.id 
            )
    else:
        form = ReservaForm() # Si el método de la solicitud no es POST, se crea una instancia vacía del formulario ReservaForm para mostrarlo al usuario y permitirle crear una nueva reserva.

     # OBTENER RESERVAS
    reservas = Reserva.objects.all().select_related('cliente', 'cancha').order_by('id')

    # FILTROS
    fecha = request.GET.get('fecha')
    cliente = request.GET.get('cliente')
    estado = request.GET.get('estado')
    cancha = request.GET.get('cancha')

    # FILTRAR POR FECHA
    if fecha:
        reservas = reservas.filter(fecha=fecha)

    # FILTRAR POR CLIENTE
    if cliente:
        reservas = reservas.filter(
            Q(cliente__nombre__icontains=cliente) |
            Q(cliente__apellido__icontains=cliente) |
            Q(cliente__dni__icontains=cliente) # Permite buscar reservas por el nombre, apellido o DNI del cliente utilizando una consulta Q para combinar las condiciones de búsqueda con un operador OR. El uso de __icontains permite realizar una búsqueda insensible a mayúsculas y minúsculas.
        )
    # FILTRAR POR ESTADO
    if estado:
        reservas = reservas.filter(
            estado=estado
        )

    # FILTRAR POR CANCHA
    if cancha:
        reservas = reservas.filter(
            cancha__id=cancha
        )

    # OBTENER CANCHAS
    canchas = Cancha.objects.all()

    return render(
        request,
        'reservas/lista_reservas.html',
        {
            'reservas': reservas,
            'form': form,
            'canchas': canchas
        }
    ) # Renderiza la plantilla 'reservas/lista_reservas.html' con el contexto que incluye la lista de reservas filtradas, el formulario para crear nuevas reservas y la lista de canchas disponibles para los filtros. Esto permite mostrar la lista de reservas al usuario y proporcionar opciones para crear nuevas reservas y filtrar las existentes.

#REGISTRAR RESERVA

@permission_required("reservas.add_reserva")
def crear_reserva(request):

    if request.method == 'POST':

        form = ReservaForm(request.POST)

        if form.is_valid():

            reserva = form.save()

            return redirect(
                'pago_create_reserva',
                reserva_id=reserva.id
            )

    else:

        form = ReservaForm()

    return render(
        request,
        'reservas/crear_reserva.html',
        {
            'form': form
        }
    )

# EDITAR RESERVA
@permission_required("reservas.change_reserva")
def editar_reserva(request, id):

    reserva = get_object_or_404(Reserva, id=id) # Obtiene la reserva con el ID proporcionado o devuelve un error 404 si no se encuentra. Esto asegura que solo se pueda editar una reserva existente y evita errores si se intenta acceder a una reserva que no existe.

    if request.method == 'POST':

        form = ReservaForm(
            request.POST,
            instance=reserva
        )

        if form.is_valid():

            form.save()

            return redirect('lista_reservas')

    else:

        form = ReservaForm(instance=reserva)

    return render(
        request,
        'reservas/editar_reserva.html',
        {
            'form': form,
            'reserva': reserva
        }
    ) # Renderiza la plantilla 'reservas/editar_reserva.html' con el contexto que incluye el formulario para editar la reserva y la propia reserva. Esto permite mostrar un formulario prellenado con los datos de la reserva existente, lo que facilita al usuario realizar cambios y guardar la reserva actualizada.




# CANCELAR RESERVA
@permission_required("reservas.delete_reserva")
def cancelar_reserva(request, id):

    reserva = get_object_or_404(
        Reserva,
        id=id
    ) # Obtiene la reserva con el ID proporcionado o devuelve un error 404 si no se encuentra. Esto asegura que solo se pueda cancelar una reserva existente y evita errores si se intenta acceder a una reserva que no existe.

    # fecha y hora actual
    ahora = datetime.now()

    # fecha y hora de la reserva
    fecha_reserva = datetime.combine(
        reserva.fecha,
        reserva.hora_inicio
    )

    diferencia = fecha_reserva - ahora # Calcula la diferencia entre la fecha y hora de la reserva y la fecha y hora actual para determinar si la cancelación se realiza dentro del plazo permitido o fuera de él.

    # -----------------------------
    # CANCELACIÓN FUERA DEL PLAZO
    # -----------------------------

    if diferencia < timedelta(hours=6): # Si la diferencia es menor a 6 horas, se considera una cancelación fuera del plazo permitido y se aplica un cargo. En este caso, se actualiza el estado de la reserva a 'CANCELADA CON CARGO' y se muestra un mensaje de error al usuario indicando que se aplicó un cargo por la cancelación tardía.

        reserva.estado = 'CANCELADA CON CARGO'

        messages.error(
            request,
            'La reserva fue cancelada fuera del plazo permitido. Se aplicó un cargo.'
        )

    # -----------------------------
    # CANCELACIÓN DENTRO DEL PLAZO
    # -----------------------------

    else:

        reserva.estado = 'CANCELADA CON REEMBOLSO'

        messages.success(
            request,
            'La reserva fue cancelada correctamente. Se procesará el reembolso.'
        )

    reserva.save()

    return redirect('lista_reservas')

@permission_required("reservas.add_reserva")
def generar_reserva_rapida(request):
    cancha_id = request.GET.get('cancha')
    fecha = request.GET.get('fecha')
    hora_inicio = request.GET.get('hora')
    cliente_id = request.GET.get('cliente') 
    
    cancha = get_object_or_404(Cancha, id=cancha_id)
    cliente = get_object_or_404(Usuario, id=cliente_id)
    
    # Calcular hora de fin (60 minutos)
    formato = '%H:%M'
    hora_inicio_dt = datetime.strptime(hora_inicio, formato)
    hora_fin_dt = hora_inicio_dt + timedelta(minutes=60)
    hora_fin = hora_fin_dt.strftime(formato)
    
    hora_inicio_objeto = hora_inicio_dt.time()
    hora_fin_objeto = hora_fin_dt.time()


    # Crear la reserva directamente
    reserva = Reserva.objects.create(
        cancha=cancha,
        fecha=fecha,
        hora_inicio=hora_inicio_objeto,
        hora_fin=hora_fin_objeto,
        cliente=cliente,
        estado='PENDIENTE',
        precio_final=cancha.tipo.precio_hora
    )
    return redirect('pago_create_reserva', reserva_id=reserva.id)


# CONSULTAR DISPONIBILIDAD
@permission_required("reservas.view_reserva")
def consultar_disponibilidad(request):
    canchas = Cancha.objects.filter(estado='DISPONIBLE') 
    reservas = None 
    horarios_libres = []
    
    # 1. Calculamos los límites de fechas (Hoy y dentro de 7 días)
    hoy_dt = datetime.today()
    max_fecha_dt = hoy_dt + timedelta(days=7)
    
    hoy_str = hoy_dt.strftime('%Y-%m-%d')
    max_fecha_str = max_fecha_dt.strftime('%Y-%m-%d')

    fecha = request.GET.get('fecha') 
    cancha_id = request.GET.get('cancha') 

    # Si ingresan una fecha, validamos que esté dentro del rango de los 7 días
    if fecha:
        try:
            fecha_seleccionada = datetime.strptime(fecha, '%Y-%m-%d')
            # Si es menor a hoy o mayor a los 7 días permitidos, la reseteamos a hoy
            if fecha_seleccionada.date() < hoy_dt.date() or fecha_seleccionada.date() > max_fecha_dt.date():
                fecha = hoy_str
        except ValueError:
            fecha = hoy_str

    clientes = Usuario.objects.all().order_by('nombre', 'apellido') 

    if fecha and cancha_id:
        reservas = Reserva.objects.filter(
            fecha=fecha,
            cancha_id=cancha_id
        ).exclude(
            estado__startswith='CANCELADA' 
        ).order_by('hora_inicio') 
        
        intervalos_ocupados = [(r.hora_inicio, r.hora_fin) for r in reservas]

        hora_actual = datetime.combine(datetime.today(), time(8, 0))
        hora_cierre = datetime.combine(datetime.today(), time(23, 0))

        while hora_actual < hora_cierre:
            inicio = hora_actual.time()
            fin = (hora_actual + timedelta(minutes=60)).time() 

            ocupado = any(
                hora_inicio_res < fin and hora_fin_res > inicio 
                for hora_inicio_res, hora_fin_res in intervalos_ocupados
            )

            if not ocupado:
                horarios_libres.append({
                    'hora_inicio': inicio.strftime('%H:%M'),
                    'texto': f"{inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')}"
                })

            hora_actual += timedelta(minutes=60)

    return render(
        request,
        'reservas/disponibilidad.html',
        {
            'canchas': canchas,
            'reservas': reservas,
            'fecha': fecha,
            'cancha_id': cancha_id,
            'horarios_libres': horarios_libres,
            'clientes': clientes,
            'hoy': hoy_str,          
            'max_fecha': max_fecha_str, }
    )

