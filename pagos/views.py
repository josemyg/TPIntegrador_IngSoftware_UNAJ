from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Pago, Recibo, TipoPago
from .forms import PagoForm
import unicodedata

def eliminar_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

class PagoUpdateView(UpdateView):
    model = Pago
    fields = ['origen_pago', 'tipo_pago', 'descuento', 'monto']
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pago_list')

class PagoDeleteView(DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pago_list')

class PagoListView(ListView):
    model = Pago
    template_name = 'pagos/pago_list.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        queryset = Pago.objects.all().select_related('tipo_pago', 'descuento')
        
        # 1. FILTRO POR ORIGEN (Cumple RF-60 a RF-63 de forma segmentada)
        # Urls posibles: /pagos/?tipo=alquiler_cancha , /pagos/?tipo=inscripcion_liga, etc.
        tipo_servicio = self.request.GET.get('tipo', '')
        if tipo_servicio:
            queryset = queryset.filter(origen_pago=tipo_servicio)

        # 2. BUSCADOR INTELIGENTE (Ignora mayúsculas y acentos en SQLite)
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
class ReciboListView(ListView):
    model = Recibo
    template_name = 'pagos/recibo_list.html'
    context_object_name = 'recibos'
    ordering = ['-id'] # Los más nuevos primero

class ReciboUpdateView(UpdateView):
    model = Recibo
    fields = ['fecha'] # Por normativa fiscal, solo se suele editar la fecha o datos de control
    template_name = 'pagos/recibo_form.html'
    success_url = reverse_lazy('recibo_list')

class ReciboDeleteView(DeleteView):
    model = Recibo
    template_name = 'pagos/recibo_confirm_delete.html'
    success_url = reverse_lazy('recibo_list')

class PagoCreateView(CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pago_list')

    def form_valid(self, form):
        #Guardamos el Pago primero
        response = super().form_valid(form)
        #Creamos el Recibo asociado en el momento de crear el Pago
        Recibo.objects.create(pago=self.object)
        return response
    
#IMPRESION

class ReciboImprimirView(DetailView):
    model = Recibo
    template_name = 'pagos/recibo_print.html'
    context_object_name = 'recibo'