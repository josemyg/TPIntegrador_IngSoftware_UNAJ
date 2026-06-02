from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,DetailView
from .models import Equipo, Liga, Torneo, Partido
from .forms import EquipoForm, LigaForm, TorneoForm
from django.shortcuts import render, redirect, get_object_or_404
import random

class EquipoListView(ListView):
	model = Equipo
	template_name = 'competiciones/equipo/equipo_list.html'
	context_object_name = 'equipos'

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

# ==========================================
# DETALLE DE TORNEO Y GENERACION DE FIXTURE
# ==========================================
class TorneoDetailView(DetailView):
    model = Torneo
    template_name = 'competiciones/torneo/torneo_detail.html'
    context_object_name = 'torneo_actual'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Pasamos los partidos ordenados a la plantilla
        contexto['partidos'] = self.object.partidos.all().order_by('id')
        return contexto

def generar_fixture_torneo(request, torneo_id):
    torneo_seleccionado = get_object_or_404(Torneo, pk=torneo_id)
    
    # 1. Seguro: Evitar regenerar si ya hay partidos
    if torneo_seleccionado.partidos.exists():
        return redirect('torneo_detail', pk=torneo_id)
        
    lista_equipos = list(torneo_seleccionado.equipos.all())
    
    # 2. Seguro: Minimo 2 equipos para que haya al menos un partido
    if len(lista_equipos) < 2:
        return redirect('torneo_detail', pk=torneo_id) 
        
    # Mezclamos para que los cruces sean al azar
    random.shuffle(lista_equipos)
    
    # Determinar el nombre de la fase segun la cantidad de equipos
    cantidad_total_equipos = len(lista_equipos)
    nombre_fase = "Fase Inicial"
    
    if cantidad_total_equipos == 2:
        nombre_fase = "Final"
    elif cantidad_total_equipos <= 4:
        nombre_fase = "Semifinales"
    elif cantidad_total_equipos <= 8:
        nombre_fase = "Cuartos de Final"
    elif cantidad_total_equipos <= 16:
        nombre_fase = "Octavos de Final"
        
    # Agrupar a los equipos de a dos para armar los cruces
    for indice_equipo in range(0, cantidad_total_equipos, 2):
        equipo_local = lista_equipos[indice_equipo]
        
        # Validamos que haya un rival (por si la cantidad de equipos es impar)
        if indice_equipo + 1 < cantidad_total_equipos:
            equipo_visitante = lista_equipos[indice_equipo + 1]
            
            # 1. Crear el partido de ida
            Partido.objects.create(
                competicion=torneo_seleccionado,
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                fase=nombre_fase
            )
            
            # 2. Si el torneo se configuro como "Ida y Vuelta", armamos la revancha invertida
            if torneo_seleccionado.es_ida_y_vuelta:
                Partido.objects.create(
                    competicion=torneo_seleccionado,
                    equipo_local=equipo_visitante, # Ahora el visitante es local
                    equipo_visitante=equipo_local, # Y el local es visitante
                    fase=f"{nombre_fase} (Vuelta)"
                )
                
    # Actualizamos el estado del torneo
    torneo_seleccionado.estado = 'En_Curso'
    torneo_seleccionado.save()
    
    return redirect('torneo_detail', pk=torneo_id)
# Create your views here.
