from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView,  TemplateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Pago, Recibo, TipoPago
from reservas.models import Reserva
from .forms import PagoForm, ReciboForm
import unicodedata
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
import io

def eliminar_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def confirmar_pago(request, pk):
    # Buscamos el pago usando su clave primaria (ID)
    pago = get_object_or_404(Pago, pk=pk)
    
    # Cambiamos el estado a PAGADO
    pago.estado = 'PAGADO'
    pago.save()
    
    # Redirigimos al usuario de vuelta al listado general de pagos
    return redirect('pago_list')


def cambiar_estado_pago(request, pk):
    """Actualiza el estado de un Pago vía POST desde la lista."""
    if request.method == 'POST':
        pago = get_object_or_404(Pago, pk=pk)
        nuevo_estado = request.POST.get('estado')
        opciones = dict(Pago.ESTADOS_PAGO).keys()
        if nuevo_estado in opciones:
            pago.estado = nuevo_estado
            pago.save()
            messages.success(request, f"Estado de Pago #{pago.id} actualizado a {pago.get_estado_display()}")
        else:
            messages.error(request, "Estado inválido")

    # Volver a la página anterior o al listado si no hay referer
    return redirect(request.META.get('HTTP_REFERER') or reverse('pago_list'))

class PagoUpdateView(UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_edit.html'
    success_url = reverse_lazy('pago_list')

class PagoDeleteView(DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pago_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Dejar que el comportamiento por defecto (CASCADE) elimine el recibo asociado al borrar el pago
        return super().delete(request, *args, **kwargs)

class PagoListView(ListView):
    model = Pago
    template_name = 'pagos/pago_list.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        queryset = Pago.objects.all().select_related('tipo_pago', 'descuento')
        
        # 1. FILTRO POR ORIGEN (Cumple RF-60 a RF-63 de forma segmentada)
        tipo_servicio = self.request.GET.get('tipo', '')
        if tipo_servicio:
            queryset = queryset.filter(origen_pago=tipo_servicio)

        # 2. BUSCADOR
        query = self.request.GET.get('b', '').strip()
        if query:
            query_limpia = eliminar_acentos(query)
            queryset = [
                pago for pago in queryset
                if query_limpia.lower() in eliminar_acentos(pago.tipo_pago.nombre).lower() or
                   query_limpia.lower() in eliminar_acentos(pago.get_origen_pago_display()).lower()
            ]
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_actual'] = self.request.GET.get('tipo', '')
        return context

#REGISTRO DE RECIBOS

def descargar_recibo_pdf(request, recibo_id):
    # 1. Buscamos el recibo real en la base de datos
    recibo = get_object_or_404(Recibo, id=recibo_id)
    
    # 2. Cargamos el archivo HTML que usás de plantilla para el comprobante
    template = get_template('pagos/comprobante_pdf.html')
    
    # 3. Le pasamos los datos del recibo al HTML (el contexto)
    context = {
        'recibo': recibo,
        'pago': recibo.pago,
    }
    html = template.render(context)
    
    # 4. Creamos un buffer en memoria para guardar el PDF temporalmente
    result = io.BytesIO()
    
    # 5. Transformamos el HTML en PDF binario
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    # Si la conversión no tuvo errores, preparamos la descarga
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        
        # 🟢 LA CLAVE DE TODO: 'attachment' fuerza la descarga con un nombre de archivo prolijo
        nombre_archivo = f"comprobante_recibo_{recibo.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        return response
        
    return HttpResponse("Error interno al generar el PDF de auditoría", status=500)


class ReciboListView(ListView):
    model = Recibo
    template_name = 'pagos/recibo_list.html'
    context_object_name = 'recibos'
    ordering = ['-id'] # Los más nuevos primero

class ReciboUpdateView(UpdateView):
    model = Recibo
    form_class = ReciboForm
    template_name = 'pagos/recibo_form.html'
    success_url = reverse_lazy('recibo_list')
    def form_valid(self, form):
        # Primero dejamos que Django guarde la nueva fecha del Recibo
        response = super().form_valid(form)
        
        # Capturamos el número que el operador tipeó en el campo artificial
        nuevo_monto = form.cleaned_data.get('monto_pago')
        
        # Buscamos el pago que está atado a este recibo y le actualizamos el valor
        pago_asociado = self.object.pago
        if pago_asociado and nuevo_monto is not None:
            pago_asociado.monto = nuevo_monto
            pago_asociado.save() # 💾 Guarda en la tabla de pagos
            
        return response

class ReciboDeleteView(DeleteView):
    model = Recibo
    template_name = 'pagos/recibo_confirm_delete.html'
    success_url = reverse_lazy('recibo_list')

class PagoCreateView(TemplateView):
    template_name = 'pagos/pago_menu.html' # Tu HTML con los 4 botones grandes

    def get(self, request, *args, **kwargs):
        # Leemos si el operador hizo clic en algún botón del selector (?origen=xxx)
        origen = request.GET.get('origen')

        if origen:
            if origen == 'alquiler_cancha':
                return redirect('lista_reservas') # Va directo al formulario de canchas de tu compañero
            elif origen == 'inscripcion_liga':
                return redirect('liga_create')    # Va al de ligas
            elif origen == 'inscripcion_torneo':
                return redirect('torneo_create')  # Va al de torneos
            elif origen == 'otros_servicios':
              return redirect('restobar_create') # Va al de restobar
        
        # Si no hay parámetro, simplemente muestra la botonera selectora
        return super().get(request, *args, **kwargs)

    """ def form_valid(self, form):
        #Guardamos el Pago primero
        response = super().form_valid(form)
        #Creamos el Recibo asociado en el momento de crear el Pago
        Recibo.objects.create(pago=self.object, fecha=Now())
        return response """
    
    

#pago reserva

class PagoReservaCreateView(CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'

    def dispatch(self, request, *args, **kwargs):

        self.reserva = get_object_or_404(
            Reserva,
            pk=self.kwargs['reserva_id']
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def get_initial(self):

        initial = super().get_initial()

        initial['monto'] = self.reserva.precio_final
        initial['origen_pago'] = 'alquiler_cancha'

        return initial

    def form_valid(self, form):

        pago = form.save(commit=False)

        pago.reserva = self.reserva
        pago.monto = self.reserva.precio_final
        pago.origen_pago = 'alquiler_cancha'
        pago.estado = 'PAGADO'

        pago.save()

        Recibo.objects.create(
            pago=pago
        )

        self.reserva.estado = 'CONFIRMADA'
        self.reserva.save()

        return redirect('lista_reservas')
    