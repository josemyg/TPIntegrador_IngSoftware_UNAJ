from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required

from .models import Descuento, TipoDescuento
from .forms import DescuentoForm, TipoDescuentoForm


class DescuentoListView(PermissionRequiredMixin, ListView):
    model = Descuento
    permission_required = 'descuentos.view_descuento'
    template_name = "descuentos/descuento_list.html"
    context_object_name = 'descuento_list'
    queryset = Descuento.objects.all()
    
class DescuentoCreateView(PermissionRequiredMixin, CreateView):
    model = Descuento
    permission_required = 'descuentos.add_descuento'
    form_class = DescuentoForm
    template_name = 'descuentos/descuento_form.html'
    success_url = reverse_lazy('descuento_list')

class DescuentoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Descuento
    permission_required = 'descuentos.change_descuento'
    form_class = DescuentoForm
    template_name = "descuentos/descuento_form.html"
    success_url = reverse_lazy('descuento_list')

class DescuentoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Descuento
    permission_required = 'descuentos.delete_descuento'
    template_name = "descuentos/descuento_delete_form.html"
    success_url = reverse_lazy('descuento_list')

class DescuentoPrintView(PermissionRequiredMixin, DetailView):
    model = Descuento
    permission_required = 'descuentos.detail_descuento'
    template_name = "descuentos/descuento_print.html"
    context_object_name = 'descuento'

@permission_required("descuentos.change_descuento")
def DescuentoBaja(request, pk):
    descuento = get_object_or_404(Descuento, pk=pk)
    descuento.darDescuento_Baja()
    return redirect('descuento_list')

class TipoDescuentoListView(PermissionRequiredMixin, ListView):
    model = TipoDescuento
    permission_required = 'descuentos.view_tipodescuento'
    template_name = "tipodescuentos/tipodescuento_list.html"
    context_object_name = 'tipodescuento_list'
    queryset = TipoDescuento.objects.all()


class TipoDescuentoCreateView(PermissionRequiredMixin, CreateView):
    model = TipoDescuento
    permission_required = 'descuentos.add_tipodescuento'
    form_class = TipoDescuentoForm
    template_name = "tipodescuentos/tipodescuento_form.html"
    success_url = reverse_lazy('tipodescuento_list')


class TipoDescuentoUpdateView(PermissionRequiredMixin, UpdateView):
    model = TipoDescuento
    permission_required = 'descuentos.change_tipodescuento'
    form_class = TipoDescuentoForm
    template_name = "tipodescuentos/tipodescuento_form.html"
    success_url = reverse_lazy('tipodescuento_list')


class TipoDescuentoDeleteView(PermissionRequiredMixin, DeleteView):
    model = TipoDescuento
    permission_required = 'descuentos.delete_tipodescuento'
    template_name = "tipodescuentos/tipodescuento_delete_form.html"
    success_url = reverse_lazy('tipodescuento_list')