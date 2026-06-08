import io, base64, qrcode, unicodedata
from xhtml2pdf import pisa

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView,  TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.db.models import Q  

from .models import Pago, Recibo, TipoPago
from descuentos.models import Descuento
from reservas.models import Reserva
from .forms import PagoForm, ReciboForm

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

class PagoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Pago
    permission_required = 'pagos.change_pago'
    form_class = PagoForm
    template_name = 'pagos/pago_edit.html'
    success_url = reverse_lazy('pago_list')

class PagoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Pago
    permission_required = 'pagos.delete_pago'
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pago_list')
    
    def form_valid(self, form):
        self.object = self.get_object()
        
        if hasattr(self.object, 'recibo'):
            messages.error(
                self.request, 
                f"No se puede eliminar el Pago #{self.object.id} porque tiene el Recibo #{self.object.recibo.id} asociado. "
                f"Por cuestiones de auditoría, primero tenés que eliminar el recibo desde el Historial de Recibos."
            )
            return redirect('pago_list')
            
        success_url = self.get_success_url()
        self.object.delete()
        
        messages.success(self.request, f"El Pago #{self.object.id} fue eliminado correctamente.")
        return redirect(success_url)



class PagoListView(PermissionRequiredMixin, ListView):
    model = Pago
    permission_required = 'pagos.view_pago'
    template_name = 'pagos/pago_list.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        # Usamos select_related para traer los datos del descuento de un solo viaje
        queryset = Pago.objects.all().select_related('tipo_pago', 'descuento', 'reserva')
        
        # 1. FILTRO POR ORIGEN
        tipo_servicio = self.request.GET.get('tipo', '')
        if tipo_servicio:
            queryset = queryset.filter(origen_pago=tipo_servicio)

        # 2. BUSCADOR OPTIMIZADO (No rompe el QuerySet)
        query = self.request.GET.get('b', '').strip()
        if query:
            # Django maneja búsquedas insensibles a mayúsculas/minúsculas con iand iunaccent si tenés la extensión.
            # Filtramos directo por el nombre del método de pago o el origen en la base de datos.
            queryset = queryset.filter(
                Q(tipo_pago__nombre__icontains=query) | 
                Q(origen_pago__icontains=query)
            )
            
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
    permission_required = 'pagos.view_recibo'
    template_name = 'recibos/recibo_list.html'
    context_object_name = 'recibos'
    ordering = ['-id'] # Los más nuevos primero

class ReciboUpdateView(PermissionRequiredMixin, UpdateView):
    model = Recibo
    permission_required = 'pagos.change_recibo'
    form_class = ReciboForm
    template_name = 'recibos/recibo_form.html'
    success_url = reverse_lazy('recibo_list')
    def form_valid(self, form):
        # Primero dejamos que Django guarde la nueva fecha del Recibo
        response = super().form_valid(form)

class ReciboDeleteView(PermissionRequiredMixin, DeleteView):
    model = Recibo
    permission_required = 'pagos.delete_recibo'
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

# class PagoReservaCreateView(PermissionRequiredMixin, CreateView):
#     model = Pago
#     permission_required = 'pagos.add_pago'
#     form_class = PagoForm
#     template_name = 'pagos/pago_form.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.reserva = get_object_or_404(
#             Reserva,
#             pk=self.kwargs['reserva_id']
#         )
#         return super().dispatch(request, *args, **kwargs)

#     def get_initial(self):
#         initial = super().get_initial()
#         initial['monto'] = self.reserva.precio_final
#         initial['origen_pago'] = 'alquiler_cancha'
#         return initial

#     def form_valid(self, form):
#         # 1. Validar duplicados de caja
#         pago_existente = Pago.objects.filter(reserva=self.reserva).exists()
#         if pago_existente:
#             messages.warning(self.request, f"La reserva de {self.reserva.cliente} ya registra movimientos de caja asociados.")
#             return redirect('lista_reservas')

#         # 2. Rescatamos la instancia sin impactar la Base de Datos todavía
#         pago = form.save(commit=False)
#         pago.reserva = self.reserva
#         pago.origen_pago = 'alquiler_cancha'
#         pago.estado = 'PAGADO'

#         # Recuperamos lo que el usuario REALMENTE seleccionó en el HTML
#         pago.tipo_pago = form.cleaned_data.get('tipo_pago')
#         pago.descuento = form.cleaned_data.get('descuento')

#         # Calculamos el monto real aplicando el descuento si es que existe
#         monto_base = float(self.reserva.precio_final)

#         if pago.descuento and getattr(pago.descuento, 'cantidad', None):
#             try:
#                 # Tu modelo guarda el porcentaje como Decimal en el campo 'cantidad'
#                 porcentaje_num = float(pago.descuento.cantidad)
                
#                 # Calculamos los pesos a restar basándonos en el precio de la reserva
#                 descuento_calculado = (monto_base * porcentaje_num) / 100.0
#                 monto_final_calculado = round(monto_base - descuento_calculado, 2)
#             except (ValueError, TypeError):
#                 monto_final_calculado = monto_base
#         else:
#             monto_final_calculado = monto_base


#         pago.monto = monto_final_calculado
#         form.cleaned_data['monto'] = monto_final_calculado


#         # Guardamos el Pago definitivo con todas las relaciones mapeadas
#         pago.save()  

#         # 3. Actualizamos estado de la reserva del cliente
#         self.reserva.estado = 'CONFIRMADA'
#         self.reserva.save()

#         # 4. Generamos comprobante oficial
#         Recibo.objects.get_or_create(pago=pago)

#         messages.success(
#             self.request, 
#             f"¡Cobro Registrado! El pago por ${pago.monto} (Método: {pago.tipo_pago}) fue procesado con éxito y la reserva quedó CONFIRMADA."
#         )
        
#         return redirect('pago_list')

class PagoReservaCreateView(PermissionRequiredMixin, CreateView):
    model = Pago
    permission_required = 'pagos.add_pago'
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'

    def dispatch(self, request, *args, **kwargs):

        reserva_id = self.kwargs.get('reserva_id') or self.kwargs.get('pk')
        
        self.reserva = get_object_or_404(
            Reserva,
            pk= reserva_id
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['monto'] = self.reserva.precio_final
        initial['origen_pago'] = 'alquiler_cancha'
        return initial
    
    def form_valid(self, form):
        # 1. Buscamos si ya existe un pago pendiente para esta reserva.
        pago_pendiente = Pago.objects.filter(reserva=self.reserva, estado='PENDIENTE').first()

        tipo_pago = form.cleaned_data.get('tipo_pago')
        descuento = form.cleaned_data.get('descuento')
        monto_base = float(self.reserva.precio_final)

        if pago_pendiente:
            pago = pago_pendiente
            pago.tipo_pago = tipo_pago
            pago.descuento = descuento
            pago.estado = 'PAGADO' # Asumimos que si el pago ya existía como PENDIENTE, ahora se confirma con el nuevo formulario
            pago.origen_pago = 'alquiler_cancha'
            pago.monto = pago.calcular_monto_con_descuento(monto_base)

        else:
            pago = form.save(commit=False)
            pago.reserva = self.reserva
            pago.origen_pago = 'alquiler_cancha'
            pago.estado = 'PAGADO'
            pago.tipo_pago = tipo_pago
            pago.descuento = descuento
            pago.monto = pago.calcular_monto_con_descuento(monto_base)

        pago.save()

        self.reserva.estado = 'CONFIRMADA'
        self.reserva.save()

        Recibo.objects.get_or_create(pago=pago)

        messages.success(
            self.request,
             f"¡Cobro Registrado! El pago por ${pago.monto} (Método: {pago.tipo_pago}) fue procesado con éxito y la reserva quedó CONFIRMADA."
           )
        
        return redirect('lista_reservas')
