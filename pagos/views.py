from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView,  TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Pago, Recibo, TipoPago
from reservas.models import Reserva
from .forms import PagoForm, ReciboForm
import unicodedata
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.core.mail import EmailMessage
import io, base64, qrcode

def eliminar_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def confirmar_pago(request, pk):
    # Buscamos el pago usando su clave primaria (ID)
    pago = get_object_or_404(Pago, pk=pk)
    
    if pago.estado != 'PAGADO':
        pago.estado = 'PAGADO'
        pago.save()
    
    # Si el pago ya tiene un recibo asociado, no hacemos nada. Si no, lo creamos automáticamente.
    Recibo.objects.get_or_create(pago=pago)
    messages.success(request, f"Pago #{pago.id} confirmado. Se emitió el recibo de cobro oficial.")
    
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

            if nuevo_estado == 'PAGADO':
                Recibo.objects.get_or_create(pago=pago)
                messages.success(request, f"Estado actualizado. Se generó el recibo para el Pago #{pago.id}.")
            else:
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

class PagoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pago_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Dejar que el comportamiento por defecto (CASCADE) elimine el recibo asociado al borrar el pago
        return super().delete(request, *args, **kwargs)

class PagoListView(PermissionRequiredMixin, ListView):
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

#envio de recibo por mail

def enviar_recibo_email(request, recibo_id):
    recibo = get_object_or_404(Recibo, id=recibo_id)
    pago = recibo.pago
    
    # 🟢 SI EL USUARIO LE DIÓ A "CONFIRMAR ENVÍO" (POST)
    if request.method == 'POST':
        # Capturamos el mail que se escribió a mano en la web
        email_destino = request.POST.get('email_cliente')
        
        if not email_destino:
            return render(request, 'pagos/enviar_mail_form.html', {
                'recibo': recibo, 
                'error': 'Por favor, ingresá un correo electrónico válido.'
            })

        # --- Tu misma lógica indestructible del PDF ---
        template = get_template('pagos/comprobante_pdf.html')
        context = {'recibo': recibo, 'pago': pago}
        html = template.render(context)
        
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        
        if pdf.err:
            return HttpResponse("Error al generar el PDF", status=500)
        
        # --- Construimos el Mail ---
        asunto = f"Comprobante de Pago #{recibo.id} — Gol Ahora"
        cuerpo = f"Hola,\n\nTe adjuntamos el comprobante de tu pago por ${pago.monto}.\n\n¡Gracias por elegir a Gol Ahora!"
        
        email = EmailMessage(subject=asunto, body=cuerpo, to=[email_destino])
        email.attach(f"comprobante_{recibo.id}.pdf", result.getvalue(), "application/pdf")
        
        # --- Despachamos ---
        email.send()
        
        # Volvemos al historial general con el deber cumplido
        return redirect('pago_list')

    # Le mostramos el formulario sencillo
    return render(request, 'pagos/enviar_mail_form.html', {'recibo': recibo})


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

def mostrar_qr_pantalla(request, pago_id):
    # 1. Buscamos el pago correspondiente
    pago = get_object_or_404(Pago, id=pago_id)
    
    # 2. Fabricamos los datos que va a contener el QR
    # Podés poner los datos de tu alias, un link de Mercado Pago simulado o texto de auditoría
    datos_qr = f"GOL AHORA\nConcepto: {pago.get_origen_pago_display()}\nMonto a Abonar: ${pago.monto}\nID Control: #{pago.id}"
    
    # 3. Generamos el QR en el aire con la librería de Python
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(datos_qr)
    qr.make(fit=True)
    
    # 4. Guardamos la imagen en un buffer de memoria como PNG
    img_qr = qr.make_image(fill_color="black", back_color="white")
    buffer_qr = io.BytesIO()
    img_qr.save(buffer_qr, format="PNG")
    
    # 5. Lo codificamos a Base64 para incrustarlo directo en la etiqueta <img> del HTML
    qr_base64 = base64.b64encode(buffer_qr.getvalue()).decode('utf-8')
    qr_data_url = f"data:image/png;base64,{qr_base64}"
    
    # 6. Renderizamos la página web pasando el pago y la imagen armada
    return render(request, 'pagos/mostrar_qr.html', {
        'pago': pago,
        'qr_code': qr_data_url
    })

class ReciboListView(PermissionRequiredMixin, ListView):
    model = Recibo
    template_name = 'recibos/recibo_list.html'
    context_object_name = 'recibos'
    ordering = ['-id'] # Los más nuevos primero

class ReciboUpdateView(UpdateView):
    model = Recibo
    form_class = ReciboForm
    template_name = 'recibos/recibo_form.html'
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
            pago_asociado.save()
            
        return response

class ReciboDeleteView(PermissionRequiredMixin, DeleteView):
    model = Recibo
    template_name = 'recibos/recibo_confirm_delete.html'
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
        
        # Si no hay parámetro, simplemente muestra la botonera selectora
        return super().get(request, *args, **kwargs)

    """ def form_valid(self, form):
        #Guardamos el Pago primero
        response = super().form_valid(form)
        #Creamos el Recibo asociado en el momento de crear el Pago
        Recibo.objects.create(pago=self.object, fecha=Now())
        return response """
    
    

#pago reserva

class PagoReservaCreateView(PermissionRequiredMixin, CreateView):
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

        pago, creado = Pago.objects.get_or_create(
            reserva=self.reserva,
            defaults={
                'monto': self.reserva.precio_final,
                'origen_pago': 'alquiler_cancha',
                'estado': 'PAGADO',
                 'tipo_pago': form.cleaned_data.get('tipo_pago'),
                 'descuento': form.cleaned_data.get('descuento'),
            })
        
        if not creado:
            return redirect('lista_reservas')
        
        Recibo.objects.get_or_create(
            pago=pago)
         

        self.reserva.estado = 'CONFIRMADA'
        self.reserva.save()

        return redirect('lista_reservas')
    