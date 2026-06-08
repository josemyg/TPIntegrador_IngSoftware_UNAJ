from django.shortcuts import render
import unicodedata
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TipoCancha, Cancha
from .forms import TipoCanchaForm, CanchaForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required


# RF-12: Registrar tipo de cancha
class TipoCanchaCreateView(PermissionRequiredMixin, CreateView):
    model = TipoCancha
    permission_required = 'canchas.add_tipocancha'
    form_class = TipoCanchaForm
    template_name = 'canchas/tipo_cancha_form.html'
    success_url = reverse_lazy('tipo_cancha_list')

# RF-13: Modificar tipo de cancha
class TipoCanchaUpdateView(PermissionRequiredMixin, UpdateView):
    model = TipoCancha
    permission_required = 'canchas.change_tipocancha'
    form_class = TipoCanchaForm 
    template_name = 'canchas/tipo_cancha_form.html'
    success_url = reverse_lazy('tipo_cancha_list')

# RF-15: Eliminar tipo de cancha
class TipoCanchaDeleteView(PermissionRequiredMixin, DeleteView):
    model = TipoCancha
    permission_required = 'canchas.delete_tipocancha'
    template_name = 'canchas/tipo_cancha_confirm_delete.html'
    success_url = reverse_lazy('tipo_cancha_list')

class TipoCanchaListView(PermissionRequiredMixin, ListView):
    model = TipoCancha
    permission_required = 'canchas.view_tipocancha'
    template_name = 'canchas/tipo_cancha_list.html'
    context_object_name = 'tipos_canchas'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('b', '').strip()
        
        queryset = TipoCancha.objects.all()

        if query:
            query_limpia = eliminar_acentos(query)
            queryset = [
                tipo for tipo in queryset
                if query_limpia.lower() in eliminar_acentos(tipo.nombreTipo).lower() or
                   query_limpia.lower() in eliminar_acentos(tipo.get_superficie_display()).lower()
            ]
            
        return queryset

def eliminar_acentos(texto):
    if not texto:
        return ""
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_limpio = "".join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_limpio

def alternar_estado_cancha(request, pk):
    tipo_cancha = get_object_or_404(TipoCancha, pk=pk)
    
    # Si está disponible la mandamos a mantenimiento, y viceversa
    if tipo_cancha.estado == 'activo':
        tipo_cancha.estado = 'mantenimiento'
    else:
        tipo_cancha.estado = 'activo'
        
    tipo_cancha.save()
    return redirect('tipo_cancha_list')

#CANCHAS
# 1. VISTA PARA LISTAR LAS CANCHAS
class CanchaListView(PermissionRequiredMixin, ListView):
    model = Cancha
    permission_required = 'canchas.view_cancha'
    template_name = 'canchas/cancha_list.html'
    context_object_name = 'canchas' 
    def get_queryset(self):
        return Cancha.objects.all()

# 2. VISTA PARA REGISTRAR UNA NUEVA CANCHA
class CanchaCreateView(PermissionRequiredMixin, CreateView):
    model = Cancha
    permission_required = 'canchas.add_cancha'
    form_class = CanchaForm
    template_name = 'canchas/cancha_form.html'
    success_url = reverse_lazy('cancha_list')  # Al terminar, vuelve al listado

class CanchaUpdateView(PermissionRequiredMixin, UpdateView):
    model = Cancha
    permission_required = 'canchas.change_cancha'
    form_class = CanchaForm
    template_name = 'canchas/cancha_form.html'
    success_url = reverse_lazy('cancha_list')

class CanchaDeleteView(PermissionRequiredMixin, DeleteView):
    model = Cancha
    permission_required = 'canchas.delete_cancha'
    template_name = 'canchas/cancha_confirm_delete.html'
    success_url = reverse_lazy('cancha_list')

@permission_required("canchas.change_cancha")
def bloquear_cancha_view(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    cancha.bloquearReservas()  # Ejecuta el método de tu diagrama
    return redirect('cancha_list')

@permission_required("canchas.change_cancha")
def activar_cancha_view(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    cancha.activarCancha()     # El método inverso para volver a habilitarla
    return redirect('cancha_list')    