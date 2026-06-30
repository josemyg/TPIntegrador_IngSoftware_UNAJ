from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm

from gestion.models import Cliente
from gestion.views import inicio
from .forms import ClienteRegistroForm
# Create your views here.

class RegistroClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteRegistroForm
    template_name = 'registro/registro_cliente_form.html'
    success_url = reverse_lazy('login')

class ContrasenaClienteResetView(auth_views.PasswordResetView):
    model = User
    form_class = PasswordResetForm
    template_name = 'registro/registro_clientepasswordreset_form.html'
    success_url = reverse_lazy('registro_cliente_exitoso')

def registro_exitoso_cliente(request):
    cliente = request.user
    nombre_cliente = cliente

    return render(request, 'registro/registro_exitoso_cliente.html', {
        'cliente': cliente,
        'contraseña': 'f.123456',
    })