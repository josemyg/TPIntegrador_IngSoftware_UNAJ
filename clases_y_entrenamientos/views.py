from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from django_filters.views import FilterView

from .models import AsistenciaClase, Entrenamiento, Clase, AsistenciaEntrenamiento
from .forms import EntrenamientoForm, ClaseForm
from .filters import ClaseFilter, EntrenamientoFilter

""" class ClaseListView(PermissionRequiredMixin, ListView):
    model = Clase
    permission_required = 'clases_y_entrenamientos.view_clase'
    template_name = 'clases_y_entrenamientos/clase/clase_list.html'
    context_object_name = 'clase_list'
    paginate_by = 10 """


class ClaseListView(PermissionRequiredMixin, FilterView):
    model = Clase
    permission_required = 'clases_y_entrenamientos.view_clase'
    filterset_class = ClaseFilter
    template_name = 'clases_y_entrenamientos/clase/clase_list.html'
    context_object_name = 'clase_list'
    queryset = Clase.objects.all()
    paginate_by = 25

class ClaseCreateView(PermissionRequiredMixin, CreateView):
    model = Clase
    permission_required = 'clases_y_entrenamientos.add_clase'
    form_class = ClaseForm
    template_name = 'clases_y_entrenamientos/clase/clase_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

    def form_valid(self, form):
        messages.success(self.request, 'Clase creada correctamente.')
        return super().form_valid(form)


class ClaseUpdateView(PermissionRequiredMixin, UpdateView):
    model = Clase
    permission_required = 'clases_y_entrenamientos.change_clase'
    form_class = ClaseForm
    template_name = 'clases_y_entrenamientos/clase/clase_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

    def form_valid(self, form):
        messages.success(self.request, 'Clase modificada correctamente.')
        return super().form_valid(form)


class ClaseDeleteView(PermissionRequiredMixin, DeleteView):
    model = Clase
    permission_required = 'clases_y_entrenamientos.delete_clase'
    template_name = 'clases_y_entrenamientos/clase/clase_confirm_delete.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Clase eliminada correctamente.')
        return super().post(request, *args, **kwargs)


class ClasePrintView(PermissionRequiredMixin, DetailView):
    model = Clase
    permission_required = 'clases_y_entrenamientos.view_clase'
    template_name = 'clases_y_entrenamientos/clase/clase_print.html'
    context_object_name = 'clase'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datos_imprimir'] = self.object.imprimir_clase()
        context['reporte_asistencia'] = self.object.generar_reporte_asistencia()
        return context


class ClaseReporteView(PermissionRequiredMixin, DetailView):
    model = Clase
    permission_required = 'clases_y_entrenamientos.view_clase'
    template_name = 'clases_y_entrenamientos/clase/clase_reporte.html'
    context_object_name = 'clase'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reporte'] = self.object.generar_reporte_clase()
        return context

@permission_required('clases_y_entrenamientos.change_clase')
def tomar_asistencia_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    
    if request.method == 'POST':
        for alumno in clase.alumnos.all():
            asistio = request.POST.get(f'alumno_{alumno.id}') == 'on'
            AsistenciaClase.generar_asistencia(clase, alumno, asistio)
        return redirect('clases_y_entrenamientos:clase_print', pk=clase.pk)
    
    return render(request, 'clases_y_entrenamientos/clase/tomar_asistencia_clase.html', {'clase': clase})

   
    


# VISTAS DE ENTRENAMIENTOS


class EntrenamientoListView(PermissionRequiredMixin, ListView):
    model = Entrenamiento
    permission_required = 'clases_y_entrenamientos.view_entrenamiento'
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_list.html'
    context_object_name = 'entrenamiento_list'
    paginate_by = 10


class EntrenamientoCreateView(PermissionRequiredMixin, CreateView):
    model = Entrenamiento
    permission_required = 'clases_y_entrenamientos.add_entrenamiento'
    form_class = EntrenamientoForm
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')

    def form_valid(self, form):
        messages.success(self.request, 'Entrenamiento creado correctamente.')
        return super().form_valid(form)


class EntrenamientoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Entrenamiento
    permission_required = 'clases_y_entrenamientos.change_entrenamiento'
    form_class = EntrenamientoForm
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')
    def form_valid(self, form):
        messages.success(self.request, 'Entrenamiento modificado correctamente.')
        return super().form_valid(form)


class EntrenamientoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Entrenamiento
    permission_required = 'clases_y_entrenamientos.delete_entrenamiento'
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_confirm_delete.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Entrenamiento eliminado correctamente.')
        return super().post(request, *args, **kwargs)


class EntrenamientoPrintView(PermissionRequiredMixin, DetailView):
    model = Entrenamiento
    permission_required = 'clases_y_entrenamientos.view_entrenamiento'
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_print.html'
    context_object_name = 'entrenamiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datos_imprimir'] = self.object.imprimir_entrenamiento()
        context['reporte_asistencia'] = self.object.generar_reporte_asistencia()
        return context


class EntrenamientoReporteView(PermissionRequiredMixin, DetailView):
    model = Entrenamiento
    permission_required = 'clases_y_entrenamientos.view_entrenamiento'
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_reporte.html'
    context_object_name = 'entrenamiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reporte'] = self.object.generar_reporte_entrenamiento()
        return context

@permission_required('clases_y_entrenamientos.change_entrenamiento')
def tomar_asistencia_entrenamiento(request, pk):
    entrenamiento = get_object_or_404(Entrenamiento, pk=pk)
    
    if request.method == 'POST':
        for alumno in entrenamiento.alumnos.all():
            asistio = request.POST.get(f'alumno_{alumno.id}') == 'on'
            AsistenciaEntrenamiento.generar_asistencia(
                entrenamiento, alumno, asistio)
        return redirect('clases_y_entrenamientos:entrenamiento_print', pk=entrenamiento.pk)
    return render(request, 'clases_y_entrenamientos/entrenamiento/tomar_asistencia_entrenamiento.html', {'entrenamiento': entrenamiento})
