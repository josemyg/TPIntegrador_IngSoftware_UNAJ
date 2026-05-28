from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import DescuentoForm
from django.shortcuts import redirect, get_object_or_404
from .models import Descuento



class DescuentoListView(ListView):
    model = Descuento
    template_name = "descuentos/descuento_list.html"
    context_object_name = 'descuento_list'
    queryset = Descuento.objects.all()
    
class DescuentoCreateView(CreateView):
    model = Descuento
    form_class = DescuentoForm
    template_name = 'descuentos/descuento_form.html'
    success_url = reverse_lazy('descuento_list')

class DescuentoUpdateView(UpdateView):
    model = Descuento
    form_class = DescuentoForm
    template_name = "descuentos/descuento_form.html"
    success_url = reverse_lazy('descuento_list')

class DescuentoDeleteView(DeleteView):
    model = Descuento
    template_name = "descuentos/descuento_delete_form.html"
    success_url = reverse_lazy('descuento_list')


class DescuentoPrintView(DetailView):
    model = Descuento
    template_name = "descuentos/descuento_print.html"
    context_object_name = 'descuento'



def DescuentoBaja(request, pk):

    descuento = get_object_or_404(Descuento, pk=pk)

    descuento.darDescuento_Baja()

    return redirect('descuento_list')


def inicio(request):
    return render(request, 'principal.html')

