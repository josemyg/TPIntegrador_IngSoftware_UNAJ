from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404

from .models import Cliente, Profesor
from .forms import ProfesorForm, ClienteForm


class ProfesorListView(PermissionRequiredMixin, ListView):
    model = Profesor
    permission_required = 'profesor.list_profesor'
    template_name = "gestion/profesor/profesor_list.html"
    context_object_name = 'profesor_list'
    #queryset = Profesor.objects.all()
    queryset = Profesor.objects.exclude(estado='baja').exclude(estado='en_validacion')
    paginate_by = 20

class ProfesoresaValidarListView(PermissionRequiredMixin, ListView):
    model = Profesor
    permission_required = 'profesor.list_profesor'
    template_name = 'gestion/profesor/profesor_list_validar.html'
    context_object_name = 'profesor_list'
    queryset = Profesor.objects.filter(estado='en_validacion')
    paginate_by = 20

class ProfesorCreateView(PermissionRequiredMixin, CreateView):
    model = Profesor
    permission_required = 'profesor.add_profesor'
    form_class = ProfesorForm
    template_name = 'gestion/profesor/profesor_form.html'
    success_url = reverse_lazy('profesor_list')

class ProfesorUpdateView(PermissionRequiredMixin, UpdateView):
    model = Profesor
    permission_required = 'profesor.update_profesor'
    form_class = ProfesorForm
    template_name = "gestion/profesor/profesor_form.html"
    success_url = reverse_lazy('profesor_list')

class ProfesorDeleteView(PermissionRequiredMixin, DeleteView):
    model = Profesor
    permission_required = 'profesor.delete_profesor'
    template_name = "gestion/profesor/profesor_delete_form.html"
    success_url = reverse_lazy('profesor_list')

class ProfesorPrintView(PermissionRequiredMixin, DetailView):
    model = Profesor
    template_name = "gestion/profesor/profesor_print.html"
    context_object_name = 'profesor'
    success_url = reverse_lazy('profesor_list')

class ProfesorVerificarView(PermissionRequiredMixin, DetailView):
    model = Profesor
    template_name = "gestion/profesor/profesor_verificador.html"
    context_object_name = 'profesor'
    success_url = reverse_lazy('profesor_list')

def ConfirmarVerificacionProfesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    profesor.verificar_estado_profesor()
    return redirect('profesoresavalidar_list')

class ClienteListView(PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = "gestion/cliente/cliente_list.html"
    context_object_name = 'cliente_list'
    paginate_by = 20
    queryset = Cliente.objects.exclude(estado='baja')

class ClienteCreateView(PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'gestion/cliente/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "gestion/cliente/cliente_form.html"
    success_url = reverse_lazy('cliente_list')

class ClienteDeleteView(PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = "gestion/cliente/cliente_delete_form.html"
    success_url = reverse_lazy('cliente_list')

class ClientePrintView(PermissionRequiredMixin, DetailView):
    model = Cliente
    template_name = "gestion/cliente/cliente_print.html"
    context_object_name = 'cliente'

def inicio(request):
    return render(request, 'principal.html')
