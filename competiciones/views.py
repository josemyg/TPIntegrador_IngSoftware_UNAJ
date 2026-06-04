from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,DetailView
from .models import Equipo, Liga, Torneo
from .forms import EquipoForm, LigaForm, TorneoForm
import random

class EquipoListView(ListView):
	model = Equipo
	template_name = 'competiciones/equipo/equipo_list.html'
	context_object_name = 'equipo_list'

class EquipoCreateView(CreateView):
	model = Equipo
	form_class = EquipoForm
	template_name = 'competiciones/equipo/equipo_form.html'
	success_url = reverse_lazy('equipo_list')

class EquipoUpdateView(UpdateView):
	model = Equipo
	form_class = EquipoForm
	template_name = 'competiciones/equipo/equipo_form.html'
	success_url = reverse_lazy('equipo_list')

class EquipoDeleteView(DeleteView):
	model = Equipo
	template_name = 'competiciones/equipo/equipo_confirm_delete.html'
	success_url = reverse_lazy('equipo_list')

class LigaListView(ListView):
    model = Liga
    template_name = 'competiciones/liga/liga_list.html'
    context_object_name = 'liga_list'

class LigaCreateView(CreateView):
    model = Liga
    form_class = LigaForm
    template_name = 'competiciones/liga/liga_form.html'
    success_url = reverse_lazy('liga_list')

class LigaUpdateView(UpdateView):
    model = Liga
    form_class = LigaForm
    template_name = 'competiciones/liga/liga_form.html'
    success_url = reverse_lazy('liga_list')

class LigaDeleteView(DeleteView):
    model = Liga
    template_name = 'competiciones/liga/liga_confirm_delete.html'
    success_url = reverse_lazy('liga_list')


# --- CRUD DE TORNEOS ---
class TorneoListView(ListView):
    model = Torneo
    template_name = 'competiciones/torneo/torneo_list.html'
    context_object_name = 'torneo_list'

class TorneoCreateView(CreateView):
    model = Torneo
    form_class = TorneoForm
    template_name = 'competiciones/torneo/torneo_form.html'
    success_url = reverse_lazy('torneo_list')

class TorneoUpdateView(UpdateView):
    model = Torneo
    form_class = TorneoForm
    template_name = 'competiciones/torneo/torneo_form.html'
    success_url = reverse_lazy('torneo_list')

class TorneoDeleteView(DeleteView):
    model = Torneo
    template_name = 'competiciones/torneo/torneo_confirm_delete.html'
    success_url = reverse_lazy('torneo_list')

# ==========================================
# DETALLE DE LIGA Y GENERACION DE FIXTURE
# ==========================================
class LigaDetailView(DetailView):
    model = Liga
    template_name = 'competiciones/liga/liga_detail.html'
    context_object_name = 'liga'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Pasamos los partidos a la plantilla
        contexto['partidos'] = self.object.partidos.all().order_by('id')
        return contexto

def generar_fixture_liga(request, liga_id):
    liga_actual = get_object_or_404(Liga, pk=liga_id)
    
    # 1. Seguro: Evitar regenerar si ya hay partidos
    if liga_actual.partidos.exists():
        return redirect('liga_detail', pk=liga_id)
        
    lista_equipos = list(liga_actual.equipos.all())
    
    # 2. Seguro: Minimo 2 equipos para jugar
    if len(lista_equipos) < 2:
        return redirect('liga_detail', pk=liga_id) 
        
    # Mezclamos para que el sorteo sea aleatorio cada vez
    random.shuffle(lista_equipos)
    
    # Si hay una cantidad impar de equipos, agregamos un equipo "Fantasma" (Libre)
    if len(lista_equipos) % 2 != 0:
        lista_equipos.append(None) 
        
    total_fechas = len(lista_equipos) - 1
    mitad_equipos = len(lista_equipos) // 2
    
    # Algoritmo Round-Robin (Todos contra Todos)
    for numero_fecha in range(total_fechas):
        for indice_equipo in range(mitad_equipos):
            equipo_local = lista_equipos[indice_equipo]
            equipo_visitante = lista_equipos[len(lista_equipos) - 1 - indice_equipo]
            
            # Si ninguno de los dos es el equipo "Fantasma", se crea el partido
            if equipo_local is not None and equipo_visitante is not None:
                # Alternamos localia para que sea justo
                if numero_fecha % 2 == 1 and indice_equipo != 0:
                    equipo_local, equipo_visitante = equipo_visitante, equipo_local
                    
                Partido.objects.create(
                    competicion=liga_actual,
                    equipo_local=equipo_local,
                    equipo_visitante=equipo_visitante,
                    fase=f"Fecha {numero_fecha + 1}"
                )
                
        # Rotar la lista dejando al primer equipo fijo
        ultimo_equipo = lista_equipos.pop()
        lista_equipos.insert(1, ultimo_equipo)
        
    # Actualizamos el estado de la liga
    liga_actual.estado = 'En_Curso'
    liga_actual.save()
    
    return redirect('liga_detail', pk=liga_id)
# Create your views here.
