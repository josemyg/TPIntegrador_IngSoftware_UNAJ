from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TipoCancha
from .forms import TipoCanchaForm
from django.db.models import Q

# RF-14: Consultar/Listar tipos de canchas
class TipoCanchaListView(ListView):
    model = TipoCancha
    template_name = 'canchas/tipo_cancha_list.html'
    context_object_name = 'tipos_canchas'

# RF-12: Registrar tipo de cancha
class TipoCanchaCreateView(CreateView):
    model = TipoCancha
    fields = ['nombre', 'superficie', 'capacidad']
    template_name = 'canchas/tipo_cancha_form.html'
    success_url = reverse_lazy('tipo_cancha_list')

# RF-13: Modificar tipo de cancha
class TipoCanchaUpdateView(UpdateView):
    model = TipoCancha
    fields = ['nombre', 'superficie', 'capacidad']
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
        queryset = super().get_queryset()
        buscar = self.request.GET.get('b')
        
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) | 
                Q(superficie__icontains=buscar)
            )
        return queryset