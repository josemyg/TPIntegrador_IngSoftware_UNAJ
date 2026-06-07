from django.shortcuts import render
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


def generar_fixture_liga(request, liga_id):
    from .models import Liga # Aseguramos el import por si acaso
    liga = get_object_or_404(Liga, id=liga_id)
    equipos = list(liga.equipos.all().order_by('id'))
    
    if len(equipos) < 2:
        messages.error(request, "Se necesitan al menos 2 equipos para armar la liga.")
        return redirect('liga_detail', pk=liga.id)
        
    # Algoritmo Round-Robin: Si hay equipos impares, agregamos un "Fantasma"
    if len(equipos) % 2 != 0:
        equipos.append(None)
        
    total_equipos = len(equipos)
    mitad = total_equipos // 2
    
    # Limpiamos fixtures anteriores para no duplicar
    Partido.objects.filter(competicion=liga).delete()
    
    # Generamos todas las fechas
    for fecha in range(1, total_equipos):
        for i in range(mitad):
            local = equipos[i]
            visitante = equipos[total_equipos - 1 - i]
            
            # Si ninguno es el Fantasma, entonces hay partido
            if local is not None and visitante is not None:
                # Alternamos la localia en las fechas pares para justicia deportiva
                if fecha % 2 == 0 and i == 0:
                    local, visitante = visitante, local
                    
                Partido.objects.create(
                    competicion=liga,
                    equipo_local=local,
                    equipo_visitante=visitante,
                    fase=f"Fecha {fecha}"
                )
        
        # Rotamos la lista dejando al primer equipo fijo (Pivote)
        equipos.insert(1, equipos.pop())
        
    liga.estado = 'En Curso'
    liga.save()
    
    messages.success(request, "Fixture de Liga generado con exito.")
    return redirect('liga_detail', pk=liga.id)

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
    template_name = 'competiciones/torneo/torneo_detail.html'
    context_object_name = 'torneo_actual'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Pasamos los partidos ordenados a la plantilla
        contexto['partidos'] = self.object.partidos.all().order_by('id')
        return contexto

def generar_fixture_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    
    # 1. Obtenemos todos los equipos ordenados por fecha de inscripcion (por ID)
    equipos = list(torneo.equipos.all().order_by('id'))
    cantidad_equipos = len(equipos)

    if cantidad_equipos < 2:
        messages.error(request, "Se necesitan al menos 2 equipos para iniciar el torneo.")
        return redirect('torneo_detail', pk=torneo.id)

    # 2. Calculamos la potencia de 2 mas cercana hacia arriba (Ej: si son 5, la potencia es 8)
    potencia_ideal = 2 ** math.ceil(math.log2(cantidad_equipos))
    
    # 3. Calculamos cuantos equipos pasan directo y cuantos juegan la fase previa
    cantidad_libres = potencia_ideal - cantidad_equipos
    
    # Los primeros en anotarse reciben el beneficio de esperar en la siguiente fase
    equipos_libres = equipos[:cantidad_libres]
    equipos_previa = equipos[cantidad_libres:]

    # 4. Determinamos el nombre de la fase
    nombres_fases = {
        2: 'Final', 
        4: 'Semifinal', 
        8: 'Cuartos de Final', 
        16: 'Octavos de Final', 
        32: 'Dieciseisavos de Final'
    }
    nombre_fase = nombres_fases.get(potencia_ideal, f'Ronda de {potencia_ideal}')

    # Borramos partidos anteriores por si se apreto el boton por error antes
    # CORRECCION: Usamos "competicion=torneo" en lugar de "torneo=torneo"
    Partido.objects.filter(competicion=torneo).delete()

    # 5. Creamos los partidos SOLO para los equipos que deben jugar la fase previa
    # Si la cantidad era par exacta (ej 4), cantidad_libres es 0 y todos entran aqui
    for i in range(0, len(equipos_previa), 2):
        # CORRECCION: Usamos "competicion=torneo" al crear
        Partido.objects.create(
            competicion=torneo,
            equipo_local=equipos_previa[i],
            equipo_visitante=equipos_previa[i+1],
            fase=nombre_fase
        )

    # Actualizamos el estado del torneo
    torneo.estado = 'En Curso'
    torneo.save()

    mensaje = f"Fixture generado con exito. "
    if cantidad_libres > 0:
        mensaje += f"{cantidad_libres} equipos pasaron directo a la siguiente ronda por orden de inscripcion."
    
    messages.success(request, mensaje)
    return redirect('torneo_detail', pk=torneo.id)

#==========================================
#    ASIGNACION DE CANCHA A PARTIDO       =
#==========================================

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

def obtener_ganador(partido):
    if partido.goles_local > partido.goles_visitante:
        return partido.equipo_local
    elif partido.goles_visitante > partido.goles_local:
        return partido.equipo_visitante
    else:
        # Si hay empate en goles, definen los penales
        penales_l = partido.penales_local or 0
        penales_v = partido.penales_visitante or 0
        if penales_l > penales_v:
            return partido.equipo_local
        elif penales_v > penales_l:
            return partido.equipo_visitante
        return None

def verificar_y_avanzar_fase(torneo):
    partidos_torneo = Partido.objects.filter(competicion=torneo)

    # Si hay algun partido no jugado, la fase actual aun no termina
    if partidos_torneo.filter(jugado=False).exists():
        return

    equipos_vivos = []
    todos_los_equipos = torneo.equipos.all().order_by('id')

    for equipo in todos_los_equipos:
        # Buscamos el ultimo partido que jugo este equipo en el torneo
        ultimo_partido = partidos_torneo.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
        ).order_by('-id').first()

        if not ultimo_partido:
            # Es un equipo libre que estaba esperando turno, sigue vivo
            equipos_vivos.append(equipo)
        else:
            # Si ya jugo, sigue vivo SOLO si gano ese ultimo partido
            if obtener_ganador(ultimo_partido) == equipo:
                equipos_vivos.append(equipo)

    cantidad_vivos = len(equipos_vivos)

    if cantidad_vivos == 1:
        # ¡Tenemos un campeon absoluto!
        torneo.estado = 'Finalizado' 
        torneo.save()
        return

    if cantidad_vivos > 1:
        nombres_fases = {
            2: 'Final',
            4: 'Semifinal',
            8: 'Cuartos de Final',
            16: 'Octavos de Final',
            32: 'Dieciseisavos de Final'
        }
        nombre_siguiente_fase = nombres_fases.get(cantidad_vivos, f'Ronda de {cantidad_vivos}')

        # Verificamos que esta fase no exista ya por seguridad
        if not partidos_torneo.filter(fase=nombre_siguiente_fase).exists():
            for i in range(0, cantidad_vivos, 2):
                Partido.objects.create(
                    competicion=torneo,
                    equipo_local=equipos_vivos[i],
                    equipo_visitante=equipos_vivos[i+1],
                    fase=nombre_siguiente_fase
                )

def cargar_resultado_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    url_anterior = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))

    # Forma 100% infalible de saber si es un torneo buscando su ID en la tabla Torneos
    es_torneo = Torneo.objects.filter(id=partido.competicion_id).exists()

    if request.method == 'POST':
        form = CargarResultadoForm(request.POST, instance=partido)
        if form.is_valid():
            partido_guardado = form.save(commit=False)

            # Validaciones estrictas de penales SOLO si comprobamos que es Torneo
            if es_torneo and partido_guardado.goles_local == partido_guardado.goles_visitante:
                penales_l = form.cleaned_data.get('penales_local')
                penales_v = form.cleaned_data.get('penales_visitante')
                
                if penales_l is None or penales_v is None:
                    messages.error(request, "El partido termino empatado. Debes ingresar el resultado de los penales.")
                    return render(request, 'competiciones/partido/cargar_resultado.html', {'form': form, 'partido': partido, 'url_anterior': url_anterior})
                
                if penales_l == penales_v:
                    messages.error(request, "Los penales no pueden terminar empatados en un torneo eliminatorio.")
                    return render(request, 'competiciones/partido/cargar_resultado.html', {'form': form, 'partido': partido, 'url_anterior': url_anterior})

            if partido_guardado.goles_local is not None and partido_guardado.goles_visitante is not None:
                partido_guardado.jugado = True

            partido_guardado.save()
            messages.success(request, "Resultado guardado correctamente.")

            # Si es torneo, le pasamos el objeto Torneo real al motor de avance
            if es_torneo:
                torneo_real = Torneo.objects.get(id=partido_guardado.competicion_id)
                verificar_y_avanzar_fase(torneo_real)

            return redirect(url_anterior)
    else:
        form = CargarResultadoForm(instance=partido)

    return render(request, 'competiciones/partido/cargar_resultado.html', {
        'form': form,
        'partido': partido,
        'url_anterior': url_anterior
    })