from django.shortcuts import render
import unicodedata
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TipoCancha, Cancha
from .forms import TipoCanchaForm, CanchaForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

# RF-14: Consultar/Listar tipos de canchas
class TipoCanchaListView(ListView):
    model = TipoCancha
    template_name = 'canchas/tipo_cancha_list.html'
    paginate_by = 20
    context_object_name = 'tipos_canchas'

# RF-12: Registrar tipo de cancha
class TipoCanchaCreateView(CreateView):
    model = TipoCancha
    form_class = TipoCanchaForm
    template_name = 'canchas/tipo_cancha_form.html'
   # 🎯 CAMBIO 1: Queremos que al guardar nos mande directo a CANCHA_LIST
    success_url = reverse_lazy('cancha_list')

    # 🟢 CAMBIO 2: La magia para crear la cancha física al mismo tiempo
    def form_valid(self, form):
        # 1. Primero dejamos que Django guarde el TipoCancha normalmente
        response = super().form_valid(form)
        nuevo_tipo = self.object  # Acá ya tenemos el TipoCancha creado con su ID
        
        # 2. Capturamos el nombre que puso el usuario en el formulario
        # (Como tu HTML usa name="nombre" para el casillero de texto)
        nombre_ingresado = self.request.POST.get('nombre')
        estado_inicial = self.request.POST.get('estado', 'activo')

        # 3. Creamos de forma automática la Cancha física mapeada a ese tipo
        Cancha.objects.create(
            nombre=nombre_ingresado,
            tipo=nuevo_tipo,  # 🔗 Guardamos la relación ForeignKey
            estado='DISPONIBLE' if estado_inicial == 'activo' else 'MANTENIMIENTO'
        )
        
        return response

# RF-13: Modificar tipo de cancha
class TipoCanchaUpdateView(UpdateView):
    model = TipoCancha
    form_class = TipoCanchaForm 
    template_name = 'canchas/tipo_cancha_form.html'
    success_url = reverse_lazy('tipo_cancha_list')

# RF-15: Eliminar tipo de cancha
class TipoCanchaDeleteView(DeleteView):
    model = TipoCancha
    template_name = 'canchas/tipo_cancha_confirm_delete.html'
    success_url = reverse_lazy('tipo_cancha_list')

class TipoCanchaListView(ListView):
    model = TipoCancha
    template_name = 'canchas/tipo_cancha_list.html'
    context_object_name = 'tipos_canchas'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('b', '').strip()
        
        queryset = TipoCancha.objects.all()

        if query:
            query_limpia = eliminar_acentos(query)
            queryset = [
                tipo for tipo in queryset
                if query_limpia.lower() in eliminar_acentos(tipo.nombre).lower() or
                   query_limpia.lower() in eliminar_acentos(tipo.get_superficie_display()).lower()
            ]
            
        return queryset

def eliminar_acentos(texto):
    if not texto:
        return ""
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_limpio = "".join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_limpio

def alternar_estado_cancha(request, pk):
    tipo_cancha = get_object_or_404(TipoCancha, pk=pk)
    
    # Si está disponible la mandamos a mantenimiento, y viceversa
    if tipo_cancha.estado == 'activo':
        tipo_cancha.estado = 'mantenimiento'
    else:
        tipo_cancha.estado = 'activo'
        
    tipo_cancha.save()
    return redirect('tipo_cancha_list')

#CANCHAS
# 1. VISTA PARA LISTAR LAS CANCHAS
class CanchaListView(ListView):
    model = Cancha
    template_name = 'canchas/cancha_list.html'
    context_object_name = 'canchas'  # Así la recorremos en el HTML

# 2. VISTA PARA REGISTRAR UNA NUEVA CANCHA
class CanchaCreateView(CreateView):
    model = Cancha
    form_class = CanchaForm  # Los campos del modelo que van al formulario
    template_name = 'canchas/cancha_form.html'
    success_url = reverse_lazy('cancha_list')  # Al terminar, vuelve al listado

class CanchaUpdateView(UpdateView):
    model = Cancha
    form_class = CanchaForm
    template_name = 'canchas/cancha_form.html'
    success_url = reverse_lazy('cancha_list')

class CanchaDeleteView(DeleteView):
    model = Cancha
    template_name = 'canchas/cancha_confirm_delete.html'
    success_url = reverse_lazy('cancha_list')

def bloquear_cancha_view(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    cancha.bloquearReservas()  # Ejecuta el método de tu diagrama
    return redirect('cancha_list')

def activar_cancha_view(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    cancha.activarCancha()     # El método inverso para volver a habilitarla
    return redirect('cancha_list')    