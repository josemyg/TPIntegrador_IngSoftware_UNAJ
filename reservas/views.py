from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva
from pagos.models import Pago, TipoPago
from canchas.models import TipoCancha
from .forms import ReservaForm
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib import messages
from django.views.generic import CreateView

# LISTAR Y CREAR RESERVAS
class ReservaCreateView(CreateView):
    # ... sus configuraciones de model, fields, template_name, etc ...

    def form_valid(self, form):
        # 1. Primero dejamos que Django guarde la reserva en la base de datos
        self.object = form.save()
        
        # 2. Buscamos una forma de pago por defecto (Ej: Efectivo o la primera que haya)
        tipo_pago_base = TipoPago.objects.first()
        
        # 3. 🚀 CLAVE: Creamos el Pago automáticamente usando los datos de la reserva
        Pago.objects.create(
            reserva=self.object,                        # Le asociamos la reserva recién creada
            monto=float(self.object.cancha.precio),     # Traemos el precio definido en el módulo de canchas
            origen_pago='alquiler_cancha',               # Seteamos tu choice obligatorio
            estado='PAGADO',                            # Lo marcamos como Pagado
            tipo_pago=tipo_pago_base                    # Le asignamos la forma de pago por defecto
        )
        
        # 4. Dejamos que continúe el flujo normal redirigiendo a get_success_url
        return super().form_valid(form)

def gestion_reservas(request):

    if request.method == 'POST': # Si el método de la solicitud es POST, significa que se está enviando un formulario para crear una nueva reserva.

        form = ReservaForm(request.POST) # Crea una instancia del formulario ReservaForm con los datos enviados en la solicitud POST.

        if form.is_valid():

            reserva = form.save()

            return redirect(
                'pago_create_reserva',
                reserva_id=reserva.id
            ) # Si el formulario es válido, se guarda la nueva reserva en la base de datos y luego se redirige al usuario a la vista de creación de pago para esa reserva específica, pasando el ID de la reserva recién creada como argumento.
    else:
        form = ReservaForm() # Si el método de la solicitud no es POST, se crea una instancia vacía del formulario ReservaForm para mostrarlo al usuario y permitirle crear una nueva reserva.

     # OBTENER RESERVAS
    reservas = Reserva.objects.all().order_by('-fecha')

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
            tipo_cancha__id=cancha
        )

    # OBTENER CANCHAS
    canchas = TipoCancha.objects.all()

    return render(
        request,
        'reservas/lista_reservas.html',
        {
            'reservas': reservas,
            'form': form,
            'canchas': canchas
        }
    ) # Renderiza la plantilla 'reservas/lista_reservas.html' con el contexto que incluye la lista de reservas filtradas, el formulario para crear nuevas reservas y la lista de canchas disponibles para los filtros. Esto permite mostrar la lista de reservas al usuario y proporcionar opciones para crear nuevas reservas y filtrar las existentes.


# EDITAR RESERVA
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

    diferencia = fecha_reserva - ahora 

    # -----------------------------
    # CANCELACIÓN FUERA DEL PLAZO
    # -----------------------------

    if diferencia < timedelta(hours=6):

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