from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Profesor
from .forms import ProfesorForm
from .models import Cliente
from .forms import ClienteForm

class ProfesorListView(ListView):
    model = Profesor
    template_name = "gestion/profesor/profesor_list.html"
    context_object_name = 'profesor_list'
    queryset = Profesor.objects.all()
    
class ProfesorCreateView(CreateView):
    model = Profesor
    #permission_required = 'Profesor.add_Profesor'
    form_class = ProfesorForm
    template_name = 'gestion/profesor/profesor_form.html'
    success_url = reverse_lazy('profesor_list')

class ProfesorUpdateView(UpdateView):
    model = Profesor
    form_class = ProfesorForm
    template_name = "gestion/profesor/profesor_form.html"
    success_url = reverse_lazy('profesor_list')

class ProfesorDeleteView(DeleteView):
    model = Profesor
    template_name = "gestion/profesor/profesor_delete_form.html"

class ClienteListView(ListView):
    model = Cliente
    template_name = "gestion/cliente/cliente_list.html"
    context_object_name = 'cliente_list'
    queryset = Cliente.objects.all()


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'gestion/cliente/cliente_form.html'
    success_url = reverse_lazy('cliente_list')


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "gestion/cliente/cliente_form.html"
    success_url = reverse_lazy('cliente_list')


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "gestion/cliente/cliente_delete_form.html"
    success_url = reverse_lazy('cliente_list')


def inicio(request):
    return render(request, 'principal.html')