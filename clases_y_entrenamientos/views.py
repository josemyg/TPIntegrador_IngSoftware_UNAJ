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
from django.contrib import messages
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template


class ClaseListView(ListView):
    model = Clase
    template_name = 'clases_y_entrenamientos/clase/clase_list.html'
    context_object_name = 'clase_list'
    paginate_by = 10


class ClaseCreateView(CreateView):
    model = Clase
    form_class = ClaseForm
    template_name = 'clases_y_entrenamientos/clase/clase_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

    def form_valid(self, form):
        messages.success(self.request, 'Clase creada correctamente.')
        return super().form_valid(form)


class ClaseUpdateView(UpdateView):
    model = Clase
    form_class = ClaseForm
    template_name = 'clases_y_entrenamientos/clase/clase_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.asistencias_clase.exists():
            form.fields.pop('alumnos')
            form.fields.pop('horario')
            form.fields.pop('cupo_maximo')
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Clase modificada correctamente.')
        return super().form_valid(form)


class ClaseDeleteView(DeleteView):
    model = Clase
    template_name = 'clases_y_entrenamientos/clase/clase_confirm_delete.html'
    success_url = reverse_lazy('clases_y_entrenamientos:clase_list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Clase eliminada correctamente.')
        return super().post(request, *args, **kwargs)


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
    if clase.estado in ['cancelada']:
        messages.error(request, f'No se puede tomar asistencia: la clase "{clase.nombre}" está {clase.get_estado_display()}.')
        return redirect('clases_y_entrenamientos:clase_list')
    if request.method == 'POST':
        for alumno in clase.alumnos.all():
            asistio = request.POST.get(f'alumno_{alumno.id}') == 'on'
            AsistenciaClase.generar_asistencia(clase, alumno, asistio)
        clase.estado = 'finalizada'
        clase.save()
        return redirect('clases_y_entrenamientos:clase_print', pk=clase.pk)
    return render(request, 'clases_y_entrenamientos/clase/tomar_asistencia_clase.html', {'clase': clase})


# VISTAS DE ENTRENAMIENTOS


class EntrenamientoListView(ListView):
    model = Entrenamiento
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_list.html'
    context_object_name = 'entrenamiento_list'
    paginate_by = 10


class EntrenamientoCreateView(CreateView):
    model = Entrenamiento
    form_class = EntrenamientoForm
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')

    def form_valid(self, form):
        messages.success(self.request, 'Entrenamiento creado correctamente.')
        return super().form_valid(form)


class EntrenamientoUpdateView(UpdateView):
    model = Entrenamiento
    form_class = EntrenamientoForm
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_form.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.asistencias_entrenamiento.exists():
            form.fields.pop('alumnos')
            form.fields.pop('horario')
            form.fields.pop('cupo_maximo')
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Entrenamiento modificado correctamente.')
        return super().form_valid(form)


class EntrenamientoDeleteView(DeleteView):
    model = Entrenamiento
    template_name = 'clases_y_entrenamientos/entrenamiento/entrenamiento_confirm_delete.html'
    success_url = reverse_lazy('clases_y_entrenamientos:entrenamiento_list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Entrenamiento eliminado correctamente.')
        return super().post(request, *args, **kwargs)


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
    if entrenamiento.estado in ['cancelado']:
        messages.error(request, f'No se puede tomar asistencia: el entrenamiento "{entrenamiento.nombre}" está {entrenamiento.get_estado_display()}.')
        return redirect('clases_y_entrenamientos:entrenamiento_list')
    if request.method == 'POST':
        for alumno in entrenamiento.alumnos.all():
            asistio = request.POST.get(f'alumno_{alumno.id}') == 'on'
            AsistenciaEntrenamiento.generar_asistencia(entrenamiento, alumno, asistio)
        entrenamiento.estado = 'finalizado'
        entrenamiento.save()
        return redirect('clases_y_entrenamientos:entrenamiento_print', pk=entrenamiento.pk)
    return render(request, 'clases_y_entrenamientos/entrenamiento/tomar_asistencia_entrenamiento.html', {'entrenamiento': entrenamiento})


def generar_pdf(template_src, context):
    template = get_template(template_src)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def reporte_clase_pdf(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    reporte = clase.generar_reporte_clase()
    return generar_pdf('clases_y_entrenamientos/clase/clase_reporte_pdf.html', {'reporte': reporte})

def reporte_entrenamiento_pdf(request, pk):
    entrenamiento = get_object_or_404(Entrenamiento, pk=pk)
    reporte = entrenamiento.generar_reporte_entrenamiento()
    return generar_pdf('clases_y_entrenamientos/entrenamiento/entrenamiento_reporte_pdf.html', {'reporte': reporte})