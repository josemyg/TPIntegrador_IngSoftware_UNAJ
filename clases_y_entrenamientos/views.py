from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Clase
from .forms import ClaseForm
from .models import AsistenciaClase
from .models import Entrenamiento
from .forms import EntrenamientoForm
from .models import AsistenciaEntrenamiento



class ClaseListView(ListView):
    model = Clase
    template_name = 'clases_y_entrenamientos/clase/clase_list.html'
    context_object_name = 'clase_list'


class ClaseCreateView(CreateView):
    model = Clase
    form_class = ClaseForm
    template_name = 'clases_y_entrenamientos/clase/clase_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

class ClaseUpdateView(UpdateView):
    model = Clase
    form_class = ClaseForm
    template_name = 'clases_y_entrenamientos/clase/clase_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')


class ClaseDeleteView(DeleteView):
    model = Clase
    template_name = 'clases_y_entrenamientos/clase/clase_confirm_delete.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

   


class ClasePrintView(DetailView):
    model = Clase
    template_name = 'clases_y_entrenamientos/clase/clase_print.html'
    context_object_name = 'clase'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datos_imprimir'] = self.object.imprimir_clase()
        context['reporte_asistencia'] = self.object.generar_reporte_asistencia()
        return context

class ClaseReporteView(DetailView):
    model = Clase
    template_name = 'clases_y_entrenamientos/clase/clase_reporte.html'
    context_object_name = 'clase'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reporte'] = self.object.generar_reporte_clase()
        return context
    
def tomar_asistencia_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if clase.estado in ['cancelada', 'finalizada']:
        return redirect('clases_y_entrenamientos:clase_list')
    if request.method == 'POST':
        for alumno in clase.alumnos.all():
            asistio = request.POST.get(f'alumno_{alumno.id}') == 'on'
            AsistenciaClase.generar_asistencia(clase, alumno, asistio)
        return redirect('clases_y_entrenamientos:clase_print', pk=clase.pk)
    return render(request, 'clases_y_entrenamientos/clase/tomar_asistencia_clase.html', {'clase': clase})



#VISTAS DE ENTRENAMIENTOS




class EntrenamientoListView(ListView):
    model = Entrenamiento
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_list.html'
    context_object_name = 'entrenamiento_list'


class EntrenamientoCreateView(CreateView):
    model = Entrenamiento
    form_class = EntrenamientoForm
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')

class EntrenamientoUpdateView(UpdateView):
    model = Entrenamiento
    form_class = EntrenamientoForm
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')


class EntrenamientoDeleteView(DeleteView):
    model = Entrenamiento
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_confirm_delete.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')

   


class EntrenamientoPrintView(DetailView):
    model = Entrenamiento
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_print.html'
    context_object_name = 'entrenamiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datos_imprimir'] = self.object.imprimir_entrenamiento()
        context['reporte_asistencia'] = self.object.generar_reporte_asistencia()
        return context


class EntrenamientoReporteView(DetailView):
    model = Entrenamiento
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_reporte.html'
    context_object_name = 'entrenamiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reporte'] = self.object.generar_reporte_entrenamiento()
        return context


def tomar_asistencia_entrenamiento(request, pk):
    entrenamiento = get_object_or_404(Entrenamiento, pk=pk)
    if entrenamiento.estado in ['cancelado', 'finalizado']:
        return redirect('clases_y_entrenamientos:entrenamiento_list')
    if request.method == 'POST':
        for alumno in entrenamiento.alumnos.all():
            asistio = request.POST.get(f'alumno_{alumno.id}') == 'on'
            AsistenciaEntrenamiento.generar_asistencia(entrenamiento, alumno, asistio)
        return redirect('clases_y_entrenamientos:entrenamiento_print', pk=entrenamiento.pk)
    return render(request, 'clases_y_entrenamientos/entrenamiento/tomar_asistencia_entrenamiento.html', {'entrenamiento': entrenamiento})

