from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout

from .models import Cliente, Profesor
from .forms import ProfesorForm, ProfesorSinValidarForm, ClienteForm


class ProfesorListView(PermissionRequiredMixin, ListView):
    model = Profesor
    permission_required = 'profesor.view_profesor'
    template_name = "gestion/profesor/profesor_list.html"
    context_object_name = 'profesor_list'
    #queryset = Profesor.objects.all()
    queryset = Profesor.objects.exclude(estado='baja').exclude(estado='en_validacion')
    paginate_by = 20

class ProfesoresaValidarListView(PermissionRequiredMixin, ListView):
    model = Profesor
    permission_required = 'profesor.view_profesor'
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
    permission_required = 'profesor.change_profesor'
    form_class = ProfesorForm
    template_name = "gestion/profesor/profesor_form.html"
    success_url = reverse_lazy('profesor_list')

class ProfesorAVerificarUpdateView(PermissionRequiredMixin, UpdateView):
    model = Profesor
    permission_required = 'profesor.change_profesor'
    form_class = ProfesorSinValidarForm
    success_url = reverse_lazy('profesoresavalidar_list')
    template_name = "gestion/profesor/profesor_sinvalidar_form.html"

class ProfesorDeleteView(PermissionRequiredMixin, DeleteView):
    model = Profesor
    permission_required = 'profesor.delete_profesor'
    template_name = "gestion/profesor/profesor_delete_form.html"
    success_url = reverse_lazy('profesor_list')

class ProfesorPrintView(PermissionRequiredMixin, DetailView):
    model = Profesor
    permission_required = 'profesor.view_profesor'
    template_name = "gestion/profesor/profesor_print.html"
    context_object_name = 'profesor'
    success_url = reverse_lazy('profesor_list')

class ProfesorVerificarView(PermissionRequiredMixin, DetailView):
    model = Profesor
    permission_required = 'profesor.view_profesor'
    template_name = "gestion/profesor/profesor_verificador.html"
    context_object_name = 'profesor'
    success_url = reverse_lazy('profesor_list')

@permission_required("gestion.change_profesor")
def ConfirmarVerificacionProfesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    profesor.verificar_estado_profesor()
    return redirect('profesoresavalidar_list')

class ClienteListView(PermissionRequiredMixin, ListView):
    model = Cliente
    permission_required = 'gestion.view_cliente'
    template_name = "gestion/cliente/cliente_list.html"
    context_object_name = 'cliente_list'
    paginate_by = 20
    queryset = Cliente.objects.exclude(estado='baja')

class ClienteCreateView(PermissionRequiredMixin, CreateView):
    model = Cliente
    permission_required = 'gestion.add_cliente'
    form_class = ClienteForm
    template_name = 'gestion/cliente/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteUpdateView(PermissionRequiredMixin, UpdateView):
    model = Cliente
    permission_required = 'gestion.change_cliente'
    form_class = ClienteForm
    template_name = "gestion/cliente/cliente_form.html"
    success_url = reverse_lazy('cliente_list')

class ClienteDeleteView(PermissionRequiredMixin, DeleteView):
    model = Cliente
    permission_required = 'gestion.delete_cliente'
    template_name = "gestion/cliente/cliente_delete_form.html"
    success_url = reverse_lazy('cliente_list')

class ClientePrintView(PermissionRequiredMixin, DetailView):
    model = Cliente
    permission_required = 'gestion.detail_cliente'
    template_name = "gestion/cliente/cliente_print.html"
    context_object_name = 'cliente'

def inicio(request):
    return render(request, 'principal.html')

