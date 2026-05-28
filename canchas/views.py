from django.shortcuts import render
import unicodedata
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TipoCancha
from .forms import TipoCanchaForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

# RF-14: Consultar/Listar tipos de canchas
class TipoCanchaListView(ListView):
    model = TipoCancha
    template_name = 'canchas/tipo_cancha_list.html'
    context_object_name = 'tipos_canchas'

# RF-12: Registrar tipo de cancha
class TipoCanchaCreateView(CreateView):
    model = TipoCancha
    form_class = TipoCanchaForm
    template_name = 'canchas/tipo_cancha_form.html'
    success_url = reverse_lazy('tipo_cancha_list')

# RF-13: Modificar tipo de cancha
class TipoCanchaUpdateView(UpdateView):
    model = TipoCancha
    form_class = TipoCanchaForm 
    template_name = 'canchas/tipo_cancha_form.html'
    success_url = reverse_lazy('tipo_cancha_list')

# RF-15: Eliminar tipo de cancha
class TipoCanchaDeleteView(DeleteView):
    model = TipoCancha
    template_name = 'canchas/tipo_cancha_confirm_delete.html'
    success_url = reverse_lazy('tipo_cancha_list')

class TipoCanchaListView(ListView):
    model = TipoCancha
    template_name = 'canchas/tipo_cancha_list.html'
    context_object_name = 'tipos_canchas'

    def get_queryset(self):
        query = self.request.GET.get('b', '').strip()
        
        queryset = TipoCancha.objects.all()

        if query:
            query_limpia = eliminar_acentos(query)
            queryset = [
                tipo for tipo in queryset
                if query_limpia.lower() in eliminar_acentos(tipo.nombre).lower() or
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