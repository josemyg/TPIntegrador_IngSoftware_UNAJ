from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,DetailView
from .models import Equipo, Liga, Torneo, Partido
from django.contrib import messages
from .forms import EquipoForm, LigaForm, TorneoForm, AsignarCanchaForm, CargarResultadoForm
from django.shortcuts import render, redirect, get_object_or_404
import math
import random
from django.db.models import Q

def obtener_tabla_posiciones(liga):
    # Preparamos un diccionario vacio para cada equipo
    equipos = liga.equipos.all()
    tabla = []
    
    for equipo in equipos:
        tabla.append({
            'equipo': equipo,
            'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0,
            'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0
        })
        
    # Diccionario de acceso rapido por ID para no hacer bucles lentos
    stats_dict = {stat['equipo'].id: stat for stat in tabla}
    
    # Buscamos solo los partidos terminados de esta liga
    partidos_jugados = Partido.objects.filter(competicion=liga, jugado=True)
    
    for partido in partidos_jugados:
        local = stats_dict[partido.equipo_local.id]
        visitante = stats_dict[partido.equipo_visitante.id]
        
        gl = partido.goles_local
        gv = partido.goles_visitante
        
        # Sumamos Partidos Jugados y Goles
        local['pj'] += 1
        visitante['pj'] += 1
        local['gf'] += gl
        local['gc'] += gv
        visitante['gf'] += gv
        visitante['gc'] += gl
        
        # Calculamos Puntos y Partidos Ganados/Empatados/Perdidos
        if gl > gv:
            local['pg'] += 1
            local['pts'] += 3
            visitante['pp'] += 1
        elif gv > gl:
            visitante['pg'] += 1
            visitante['pts'] += 3
            local['pp'] += 1
        else:
            local['pe'] += 1
            visitante['pe'] += 1
            local['pts'] += 1
            visitante['pts'] += 1
            
    # Calculamos la Diferencia de Goles y ordenamos la tabla
    for stat in tabla:
        stat['dg'] = stat['gf'] - stat['gc']
        
    # Python ordena primero por Puntos, luego por Diferencia de Goles, luego por Goles a Favor
    tabla.sort(key=lambda x: (x['pts'], x['dg'], x['gf']), reverse=True)
    
    return tabla

@permission_required('competiciones.change_liga')
@permission_required("competiciones.change_liga")
def generar_fixture_liga(request, pk):
    liga_actual = get_object_or_404(Liga, pk=pk)
    
    if liga_actual.partidos.exists():
        return redirect('liga_detail', pk=pk)
        
    lista_equipos = list(liga_actual.equipos.all())
    
    if len(lista_equipos) < 2:
        return redirect('liga_detail', pk=pk) 
        
    random.shuffle(lista_equipos)
    
    if len(lista_equipos) % 2 != 0:
        lista_equipos.append(None) 
        
    total_fechas = len(lista_equipos) - 1
    mitad_equipos = len(lista_equipos) // 2
    
    # 1. Generamos la Primera Rueda
    for numero_fecha in range(total_fechas):
        for indice_equipo in range(mitad_equipos):
            equipo_local = lista_equipos[indice_equipo]
            equipo_visitante = lista_equipos[len(lista_equipos) - 1 - indice_equipo]
            
            if equipo_local is not None and equipo_visitante is not None:
                if numero_fecha % 2 == 1 and indice_equipo != 0:
                    equipo_local, equipo_visitante = equipo_visitante, equipo_local
                    
                Partido.objects.create(
                    competicion=liga_actual,
                    equipo_local=equipo_local,
                    equipo_visitante=equipo_visitante,
                    fase=f"Fecha {numero_fecha + 1}"
                )
        ultimo_equipo = lista_equipos.pop()
        lista_equipos.insert(1, ultimo_equipo)
        
    # 2. NUEVO: Generamos la Segunda Rueda (Vuelta) si esta tildado
    if getattr(liga_actual, 'es_ida_y_vuelta', False):
        partidos_primera = Partido.objects.filter(competicion=liga_actual).order_by('id')
        
        for p in partidos_primera:
            num_fecha_original = int(p.fase.split(' ')[1]) # Extrae el numero de la fecha
            nueva_fecha = num_fecha_original + total_fechas
            
            Partido.objects.create(
                competicion=liga_actual,
                equipo_local=p.equipo_visitante, # Invertimos localia
                equipo_visitante=p.equipo_local, # Invertimos localia
                fase=f"Fecha {nueva_fecha}"
            )
            
    liga_actual.estado = 'En_Curso'
    liga_actual.save()
    
    return redirect('liga_detail', pk=pk)

class EquipoListView(PermissionRequiredMixin, ListView):
    model = Equipo
    permission_required = 'competiciones.view_equipo'
    template_name = 'competiciones/equipo/equipo_list.html'
    context_object_name = 'equipo_list'

class EquipoCreateView(PermissionRequiredMixin, CreateView):
    model = Equipo
    permission_required = 'competiciones.add_equipo'
    form_class = EquipoForm
    template_name = 'competiciones/equipo/equipo_form.html'
    success_url = reverse_lazy('equipo_list')
    
class EquipoUpdateView(UpdateView):
    model = Equipo
    permission_required = 'competiciones.change_equipo'
    form_class = EquipoForm
    template_name = 'competiciones/equipo/equipo_form.html'
    success_url = reverse_lazy('equipo_list')

class EquipoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Equipo
    permission_required = 'competiciones.delete_equipo'
    template_name = 'competiciones/equipo/equipo_confirm_delete.html'
    success_url = reverse_lazy('equipo_list')

class LigaListView(PermissionRequiredMixin, ListView):
    model = Liga
    permission_required = 'competiciones.view_liga'
    template_name = 'competiciones/liga/liga_list.html'
    context_object_name = 'liga_list'

class LigaCreateView(PermissionRequiredMixin, CreateView):
    model = Liga
    permission_required = 'competiciones.add_liga'
    form_class = LigaForm
    template_name = 'competiciones/liga/liga_form.html'
    success_url = reverse_lazy('liga_list')

class LigaUpdateView(PermissionRequiredMixin, UpdateView):
    model = Liga
    permission_required = 'competiciones.change_liga'
    form_class = LigaForm
    template_name = 'competiciones/liga/liga_form.html'
    success_url = reverse_lazy('liga_list')

class LigaDeleteView(PermissionRequiredMixin, DeleteView):
    model = Liga
    permission_required = 'competiciones.delete_liga'
    template_name = 'competiciones/liga/liga_confirm_delete.html'
    success_url = reverse_lazy('liga_list')


# --- CRUD DE TORNEOS ---
class TorneoListView(PermissionRequiredMixin, ListView):
    model = Torneo
    permission_required = 'competiciones.view_torneo'
    template_name = 'competiciones/torneo/torneo_list.html'
    context_object_name = 'torneo_list'

class TorneoCreateView(PermissionRequiredMixin, CreateView):
    model = Torneo
    permission_required = 'competiciones.add_liga'
    form_class = TorneoForm
    template_name = 'competiciones/torneo/torneo_form.html'
    success_url = reverse_lazy('torneo_list')

class TorneoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Torneo
    permission_required = 'competiciones.change_torneo'
    form_class = TorneoForm
    template_name = 'competiciones/torneo/torneo_form.html'
    success_url = reverse_lazy('torneo_list')

class TorneoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Torneo
    permission_required = 'competiciones.delete_torneo'
    template_name = 'competiciones/torneo/torneo_confirm_delete.html'
    success_url = reverse_lazy('torneo_list')

# ==========================================
# DETALLE DE LIGA Y GENERACION DE FIXTURE
# ==========================================
class LigaDetailView(PermissionRequiredMixin, DetailView):
    model = Liga
    permission_required = 'competiciones.view_liga'
    template_name = 'competiciones/liga/liga_detail.html'
    context_object_name = 'liga'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Enviamos los partidos y la tabla calculada en tiempo real
        context['partidos'] = Partido.objects.filter(competicion=self.object).order_by('id')
        context['tabla_posiciones'] = obtener_tabla_posiciones(self.object)
        return context

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
    permission_required = 'competiciones.view_torneo'
    template_name = 'competiciones/torneo/torneo_detail.html'
    context_object_name = 'torneo_actual'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Pasamos los partidos ordenados a la plantilla
        contexto['partidos'] = self.object.partidos.all().order_by('id')
        return contexto



#==========================================
#    ASIGNACION DE CANCHA A PARTIDO       =
#==========================================

@permission_required('competiciones.change_partido')
def asignar_cancha_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)

    if request.method == 'POST':
        form = AsignarCanchaForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, "Cancha y horario asignados correctamente.")
            # Redirigimos a la url
            url_anterior = request.POST.get('next', '/')
            return redirect(url_anterior)
    else:
        form = AsignarCanchaForm(instance=partido)

    # Le pasamos de donde vino el usuario para poder volver a esa pantalla
    url_anterior = request.META.get('HTTP_REFERER', '/')

    return render(request, 'competiciones/partido/asignar_cancha.html', {
        'form': form,
        'partido': partido,
        'url_anterior': url_anterior
    })
def evaluar_equipo_avanza(equipo, torneo):
    # Busca los partidos jugados por este equipo en el torneo actual
    partidos = Partido.objects.filter(
        competicion=torneo,
        jugado=True
    ).filter(Q(equipo_local=equipo) | Q(equipo_visitante=equipo)).order_by('-id')
    
    if not partidos.exists():
        return True # Es un equipo libre ("Bye") que todavia no jugo, sigue vivo
        
    ultimo_partido = partidos.first()
    
    # Limpiamos los textos para agrupar los partidos de la misma llave (Ej: "Semifinal")
    fase_base = ultimo_partido.fase.replace(" (Ida)", "").replace(" (Vuelta)", "")
    partidos_llave = partidos.filter(fase__startswith=fase_base)
    
    goles_favor = 0
    goles_contra = 0
    penales_favor = 0
    penales_contra = 0
    
    # Sumamos el global de la llave
    for p in partidos_llave:
        if p.equipo_local == equipo:
            goles_favor += p.goles_local
            goles_contra += p.goles_visitante
            penales_favor += (p.penales_local or 0)
            penales_contra += (p.penales_visitante or 0)
        else:
            goles_favor += p.goles_visitante
            goles_contra += p.goles_local
            penales_favor += (p.penales_visitante or 0)
            penales_contra += (p.penales_local or 0)
            
    # Evaluamos quien pasa
    if goles_favor > goles_contra:
        return True
    elif goles_contra > goles_favor:
        return False
    else:
        # Si el global termina en empate, definen los penales de la vuelta
        return penales_favor > penales_contra


def verificar_y_avanzar_fase(torneo):
    partidos_torneo = Partido.objects.filter(competicion=torneo)

    if partidos_torneo.filter(jugado=False).exists():
        return

    equipos_vivos = []
    todos_los_equipos = torneo.equipos.all().order_by('id')

    for equipo in todos_los_equipos:
        # Usamos el nuevo evaluador global
        if evaluar_equipo_avanza(equipo, torneo):
            equipos_vivos.append(equipo)

    cantidad_vivos = len(equipos_vivos)

    if cantidad_vivos == 1:
        torneo.estado = 'Finalizado' 
        torneo.save()
        return

    if cantidad_vivos > 1:
        nombres_fases = {
            2: 'Final', 4: 'Semifinal', 8: 'Cuartos de Final', 16: 'Octavos de Final', 32: 'Dieciseisavos de Final'
        }
        nombre_siguiente_fase = nombres_fases.get(cantidad_vivos, f'Ronda de {cantidad_vivos}')
        es_ida_vuelta = getattr(torneo, 'es_ida_y_vuelta', False)

        if not partidos_torneo.filter(fase__startswith=nombre_siguiente_fase).exists():
            for i in range(0, cantidad_vivos, 2):
                local = equipos_vivos[i]
                visitante = equipos_vivos[i+1]
                
                if es_ida_vuelta:
                    Partido.objects.create(competicion=torneo, equipo_local=local, equipo_visitante=visitante, fase=f"{nombre_siguiente_fase} (Ida)")
                    Partido.objects.create(competicion=torneo, equipo_local=visitante, equipo_visitante=local, fase=f"{nombre_siguiente_fase} (Vuelta)")
                else:
                    Partido.objects.create(competicion=torneo, equipo_local=local, equipo_visitante=visitante, fase=nombre_siguiente_fase)


@permission_required('competiciones.change_torneo')
def generar_fixture_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    equipos = list(torneo.equipos.all().order_by('id'))
    cantidad_equipos = len(equipos)

    if cantidad_equipos < 2:
        messages.error(request, "Se necesitan al menos 2 equipos para iniciar el torneo.")
        return redirect('torneo_detail', pk=torneo.id)

    import math
    potencia_ideal = 2 ** math.ceil(math.log2(cantidad_equipos))
    cantidad_libres = potencia_ideal - cantidad_equipos
    
    equipos_libres = equipos[:cantidad_libres]
    equipos_previa = equipos[cantidad_libres:]

    nombres_fases = {
        2: 'Final', 4: 'Semifinal', 8: 'Cuartos de Final', 16: 'Octavos de Final', 32: 'Dieciseisavos de Final'
    }
    nombre_fase = nombres_fases.get(potencia_ideal, f'Ronda de {potencia_ideal}')

    Partido.objects.filter(competicion=torneo).delete()
    es_ida_vuelta = getattr(torneo, 'es_ida_y_vuelta', False)

    for i in range(0, len(equipos_previa), 2):
        local = equipos_previa[i]
        visitante = equipos_previa[i+1]
        
        if es_ida_vuelta:
            Partido.objects.create(competicion=torneo, equipo_local=local, equipo_visitante=visitante, fase=f"{nombre_fase} (Ida)")
            Partido.objects.create(competicion=torneo, equipo_local=visitante, equipo_visitante=local, fase=f"{nombre_fase} (Vuelta)")
        else:
            Partido.objects.create(competicion=torneo, equipo_local=local, equipo_visitante=visitante, fase=nombre_fase)

    torneo.estado = 'En Curso'
    torneo.save()

    mensaje = f"Fixture generado con exito. "
    if cantidad_libres > 0:
        mensaje += f"{cantidad_libres} equipos pasaron directo a la siguiente ronda por orden de inscripcion."
    
    messages.success(request, mensaje)
    return redirect('torneo_detail', pk=torneo.id)


@permission_required('competiciones.change_partido')
def cargar_resultado_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    url_anterior = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    es_torneo = Torneo.objects.filter(id=partido.competicion_id).exists()

    if request.method == 'POST':
        form = CargarResultadoForm(request.POST, instance=partido)
        if form.is_valid():
            partido_guardado = form.save(commit=False)

            if es_torneo:
                torneo_real = Torneo.objects.get(id=partido_guardado.competicion_id)
                es_ida_vuelta = getattr(torneo_real, 'es_ida_y_vuelta', False)
                es_ida = "(Ida)" in partido.fase
                es_vuelta = "(Vuelta)" in partido.fase
                
                requiere_penales = False
                
                # Inteligencia del arbitro: ¿Cuando pedir penales?
                if es_ida_vuelta:
                    if es_vuelta:
                        # Si es la vuelta, calculamos como va el marcador global
                        fase_ida = partido.fase.replace("(Vuelta)", "(Ida)")
                        partido_ida = Partido.objects.filter(
                            competicion=torneo_real,
                            fase=fase_ida,
                            equipo_local=partido.equipo_visitante,
                            equipo_visitante=partido.equipo_local
                        ).first()
                        
                        if partido_ida:
                            global_local_actual = partido_guardado.goles_local + partido_ida.goles_visitante
                            global_visitante_actual = partido_guardado.goles_visitante + partido_ida.goles_local
                            if global_local_actual == global_visitante_actual:
                                requiere_penales = True
                else:
                    if partido_guardado.goles_local == partido_guardado.goles_visitante:
                        requiere_penales = True
                        
                if requiere_penales:
                    penales_l = form.cleaned_data.get('penales_local')
                    penales_v = form.cleaned_data.get('penales_visitante')
                    
                    if penales_l is None or penales_v is None:
                        messages.error(request, "El resultado global termino empatado. Debes ingresar los penales.")
                        return render(request, 'competiciones/partido/cargar_resultado.html', {'form': form, 'partido': partido, 'url_anterior': url_anterior})
                    if penales_l == penales_v:
                        messages.error(request, "Los penales no pueden terminar empatados.")
                        return render(request, 'competiciones/partido/cargar_resultado.html', {'form': form, 'partido': partido, 'url_anterior': url_anterior})

            if partido_guardado.goles_local is not None and partido_guardado.goles_visitante is not None:
                partido_guardado.jugado = True

            partido_guardado.save()
            messages.success(request, "Resultado guardado correctamente.")

            if es_torneo:
                verificar_y_avanzar_fase(torneo_real)

            return redirect(url_anterior)
    else:
        form = CargarResultadoForm(instance=partido)

    return render(request, 'competiciones/partido/cargar_resultado.html', {'form': form, 'partido': partido, 'url_anterior': url_anterior})