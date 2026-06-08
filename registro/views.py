from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy

from gestion.models import Cliente
from gestion.views import inicio
from .forms import ClienteRegistroForm
# Create your views here.

class RegistroClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteRegistroForm
    template_name = 'registro/registro_cliente_form.html'
    success_url = reverse_lazy('dashboard_bienvenida')

