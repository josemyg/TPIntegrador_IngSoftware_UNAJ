from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import DescuentoForm, TipoDescuentoForm
from django.shortcuts import redirect, get_object_or_404
from .models import Descuento, TipoDescuento



class DescuentoListView(PermissionRequiredMixin, ListView):
    model = Descuento
    template_name = "descuentos/descuento_list.html"
    context_object_name = 'descuento_list'
    queryset = Descuento.objects.all()
    
class DescuentoCreateView(PermissionRequiredMixin, CreateView):
    model = Descuento
    form_class = DescuentoForm
    template_name = 'descuentos/descuento_form.html'
    success_url = reverse_lazy('descuento_list')

class DescuentoUpdateView(UpdateView):
    model = Descuento
    form_class = DescuentoForm
    template_name = "descuentos/descuento_form.html"
    success_url = reverse_lazy('descuento_list')

class DescuentoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Descuento
    template_name = "descuentos/descuento_delete_form.html"
    success_url = reverse_lazy('descuento_list')


class DescuentoPrintView(PermissionRequiredMixin, DetailView):
    model = Descuento
    template_name = "descuentos/descuento_print.html"
    context_object_name = 'descuento'


def DescuentoBaja(request, pk):
    descuento = get_object_or_404(Descuento, pk=pk)
    descuento.darDescuento_Baja()
    return redirect('descuento_list')

class TipoDescuentoListView(PermissionRequiredMixin, ListView):
    model = TipoDescuento
    template_name = "tipodescuentos/tipodescuento_list.html"
    context_object_name = 'tipodescuento_list'
    queryset = TipoDescuento.objects.all()


class TipoDescuentoCreateView(PermissionRequiredMixin, CreateView):
    model = TipoDescuento
    form_class = TipoDescuentoForm
    template_name = "tipodescuentos/tipodescuento_form.html"
    success_url = reverse_lazy('tipodescuento_list')


class TipoDescuentoUpdateView(UpdateView):
    model = TipoDescuento
    form_class = TipoDescuentoForm
    template_name = "tipodescuentos/tipodescuento_form.html"
    success_url = reverse_lazy('tipodescuento_list')


class TipoDescuentoDeleteView(PermissionRequiredMixin, DeleteView):
    model = TipoDescuento
    template_name = "tipodescuentos/tipodescuento_delete_form.html"
    success_url = reverse_lazy('tipodescuento_list')



def inicio(request):
    return render(request, 'principal.html')

