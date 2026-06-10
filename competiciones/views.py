from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
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
from functools import cmp_to_key

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
    template_name = 'competiciones/equipo/equipo_confirm_delete.html'
    success_url = reverse_lazy('equipo_list')
    permission_required = 'competiciones.delete_equipo'

    # NUEVO: Revisamos todas las conexiones antes de dejarlo borrar
    def dispatch(self, request, *args, **kwargs):
        id_del_equipo = kwargs.get('pk')
        equipo_a_evaluar = get_object_or_404(Equipo, pk=id_del_equipo)
        
        # Buscamos si el equipo esta atrapado en alguna relacion oficial
        esta_en_liga = Liga.objects.filter(equipos=equipo_a_evaluar).exists()
        esta_en_torneo = Torneo.objects.filter(equipos=equipo_a_evaluar).exists()
        tiene_partidos = Partido.objects.filter(equipo_local=equipo_a_evaluar).exists() or Partido.objects.filter(equipo_visitante=equipo_a_evaluar).exists()
        
        if esta_en_liga or esta_en_torneo or tiene_partidos:
            messages.error(request, "Integridad de Datos: No puedes eliminar este equipo porque forma parte de competiciones oficiales o tiene partidos registrados.")
            return redirect('equipo_list') 
            
        return super().dispatch(request, *args, **kwargs)

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
    form_class = LigaForm
    template_name = 'competiciones/liga/liga_form.html'
    permission_required = 'competiciones.change_liga'

    # Le indicamos a Django hacia donde navegar despues de guardar
    def get_success_url(self):
        return reverse_lazy('liga_detail', kwargs={'pk': self.object.pk})

    # Interceptamos la peticion leyendo la URL directamente
    def dispatch(self, request, *args, **kwargs):
        id_de_la_liga = kwargs.get('pk')
        liga_a_editar = get_object_or_404(Liga, pk=id_de_la_liga)
        
        # Si la liga ya tiene partidos generados, bloqueamos la edicion
        if liga_a_editar.partidos.exists():
            messages.error(request, "Seguridad de Datos: No puedes modificar los equipos ni las reglas de una liga que ya tiene el fixture generado.")
            return redirect('liga_detail', pk=id_de_la_liga)
            
        return super().dispatch(request, *args, **kwargs)

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
        contexto_de_la_vista = super().get_context_data(**kwargs)
        
        # Pasamos los partidos a la plantilla
        contexto_de_la_vista['partidos'] = self.object.partidos.all().order_by('id')
        
        # Inyectamos nuestra tabla
        contexto_de_la_vista['tabla_de_posiciones'] = calcular_tabla_posiciones_oficial(self.object)
        
        return contexto_de_la_vista

@permission_required("competiciones.change_liga")
def generar_fixture_liga(request, liga_id):
    liga_actual = get_object_or_404(Liga, pk=liga_id)
    
    # 1. En lugar de bloquear, borramos el fixture anterior para regenerar todo
    Partido.objects.filter(competicion=liga_actual).delete()
        
    lista_equipos = list(liga_actual.equipos.all())
    
    # 2. Seguro: Minimo 2 equipos para jugar
    if len(lista_equipos) < 2:
        messages.error(request, "Se necesitan al menos 2 equipos para generar el fixture.")
        return redirect('liga_detail', pk=liga_id) 
        
    # Mezclamos para que el sorteo sea aleatorio cada vez
    random.shuffle(lista_equipos)
    
    # Si hay una cantidad impar de equipos, agregamos un equipo "Fantasma" (Libre)
    if len(lista_equipos) % 2 != 0:
        lista_equipos.append(None) 
        
    total_fechas = len(lista_equipos) - 1
    mitad_equipos = len(lista_equipos) // 2
    
    # Algoritmo Round-Robin (Todos contra Todos) - PRIMERA RUEDA
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

    # 3. Generamos la Segunda Rueda (Vuelta) si esta tildado el casillero
    if getattr(liga_actual, 'es_ida_y_vuelta', False):
        # Envolver en list() es vital para asegurar los datos y evitar bucles infinitos
        partidos_primera = list(Partido.objects.filter(competicion=liga_actual).order_by('id'))
        
        for p in partidos_primera:
            # Extraemos el numero de la fecha original (Ej: de "Fecha 1" saca el "1")
            num_fecha_original = int(p.fase.split(' ')[1])
            nueva_fecha = num_fecha_original + total_fechas
            
            Partido.objects.create(
                competicion=liga_actual,
                equipo_local=p.equipo_visitante, # Invertimos localia
                equipo_visitante=p.equipo_local, # Invertimos localia
                fase=f"Fecha {nueva_fecha}"
            )
        
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
    partido_evaluado = get_object_or_404(Partido, id=partido_id)
    
    url_de_retorno = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    
    # El sistema detecta de que tipo de competicion estamos hablando
    es_un_torneo = Torneo.objects.filter(id=partido_evaluado.competicion_id).exists()

    if request.method == 'POST':
        formulario_resultado = CargarResultadoForm(request.POST, instance=partido_evaluado)
        if formulario_resultado.is_valid():
            partido_guardado = formulario_resultado.save(commit=False)

            if es_un_torneo:
                # ==========================================
                # LOGICA DE TORNEOS (Requiere desempate)
                # ==========================================
                torneo_vinculado = Torneo.objects.get(id=partido_guardado.competicion_id)
                es_ida_y_vuelta = getattr(torneo_vinculado, 'es_ida_y_vuelta', False)
                es_partido_de_vuelta = "(Vuelta)" in partido_evaluado.fase
                requiere_penales = False
                
                if es_ida_y_vuelta:
                    if es_partido_de_vuelta:
                        fase_de_ida = partido_evaluado.fase.replace("(Vuelta)", "(Ida)")
                        partido_de_ida = Partido.objects.filter(
                            competicion=torneo_vinculado,
                            fase=fase_de_ida,
                            equipo_local=partido_evaluado.equipo_visitante,
                            equipo_visitante=partido_evaluado.equipo_local
                        ).first()
                        
                        if partido_de_ida:
                            goles_globales_local = partido_guardado.goles_local + partido_de_ida.goles_visitante
                            goles_globales_visitante = partido_guardado.goles_visitante + partido_de_ida.goles_local
                            if goles_globales_local == goles_globales_visitante:
                                requiere_penales = True
                else:
                    if partido_guardado.goles_local == partido_guardado.goles_visitante:
                        requiere_penales = True
                
                # Validamos que si se requieren penales, esten cargados
                if requiere_penales:
                    penales_del_local = partido_guardado.penales_local
                    penales_del_visitante = partido_guardado.penales_visitante
                    
                    if penales_del_local is None or penales_del_visitante is None:
                        messages.error(request, "El resultado global termino empatado. Debes ingresar los penales.")
                        return render(request, 'competiciones/partido/cargar_resultado.html', {
                            'form': formulario_resultado, 
                            'partido': partido_evaluado, 
                            'url_anterior': url_de_retorno,
                            'es_un_torneo': es_un_torneo
                        })
                    
                    if penales_del_local == penales_del_visitante:
                        messages.error(request, "Los penales no pueden terminar empatados.")
                        return render(request, 'competiciones/partido/cargar_resultado.html', {
                            'form': formulario_resultado, 
                            'partido': partido_evaluado, 
                            'url_anterior': url_de_retorno,
                            'es_un_torneo': es_un_torneo
                        })
            else:
                # ==========================================
                # LOGICA DE LIGAS (El empate es valido)
                # ==========================================
                # Forzamos los penales a nulo por seguridad para no ensuciar la base de datos
                partido_guardado.penales_local = None
                partido_guardado.penales_visitante = None

            # Guardado final unificado
            if partido_guardado.goles_local is not None and partido_guardado.goles_visitante is not None:
                partido_guardado.jugado = True

            partido_guardado.save()
            messages.success(request, "Resultado guardado correctamente.")

            # Si es torneo, le avisamos al motor que verifique quien avanza
            if es_un_torneo:
                verificar_y_avanzar_fase(torneo_vinculado)

            return redirect(url_de_retorno)
    else:
        formulario_resultado = CargarResultadoForm(instance=partido_evaluado)

    return render(request, 'competiciones/partido/cargar_resultado.html', {
        'form': formulario_resultado, 
        'partido': partido_evaluado, 
        'url_anterior': url_de_retorno,
        'es_un_torneo': es_un_torneo  # Variable inyectada
    })

def calcular_tabla_posiciones_oficial(liga_evaluada):
    equipos_participantes = list(liga_evaluada.equipos.all())
    diccionario_estadisticas = {}

    # Preparamos el casillero vacio para cada equipo
    for equipo_actual in equipos_participantes:
        diccionario_estadisticas[equipo_actual.id] = {
            'equipo': equipo_actual,
            'puntos_totales': 0,
            'diferencia_de_goles': 0,
            'goles_a_favor': 0,
            'goles_en_contra': 0,
            'partidos_jugados': 0
        }

    # Obtenemos todos los partidos que ya tienen resultado cargado
    todos_los_partidos_jugados = list(Partido.objects.filter(
        competicion=liga_evaluada, 
        jugado=True
    ))

    # Sumamos los puntos y goles basicos de la temporada regular
    for partido_finalizado in todos_los_partidos_jugados:
        # Los partidos de desempate no suman puntos a la tabla general, se evaluan al final
        if "Desempate" in partido_finalizado.fase:
            continue

        id_local = partido_finalizado.equipo_local.id
        id_visitante = partido_finalizado.equipo_visitante.id

        diccionario_estadisticas[id_local]['partidos_jugados'] += 1
        diccionario_estadisticas[id_visitante]['partidos_jugados'] += 1

        diccionario_estadisticas[id_local]['goles_a_favor'] += partido_finalizado.goles_local
        diccionario_estadisticas[id_local]['goles_en_contra'] += partido_finalizado.goles_visitante
        
        diccionario_estadisticas[id_visitante]['goles_a_favor'] += partido_finalizado.goles_visitante
        diccionario_estadisticas[id_visitante]['goles_en_contra'] += partido_finalizado.goles_local

        if partido_finalizado.goles_local > partido_finalizado.goles_visitante:
            diccionario_estadisticas[id_local]['puntos_totales'] += liga_evaluada.puntos_victoria
        elif partido_finalizado.goles_local < partido_finalizado.goles_visitante:
            diccionario_estadisticas[id_visitante]['puntos_totales'] += liga_evaluada.puntos_victoria
        else:
            diccionario_estadisticas[id_local]['puntos_totales'] += liga_evaluada.puntos_empate
            diccionario_estadisticas[id_visitante]['puntos_totales'] += liga_evaluada.puntos_empate

    # Calculamos la diferencia de goles final para cada equipo
    for id_equipo in diccionario_estadisticas:
        goles_favor = diccionario_estadisticas[id_equipo]['goles_a_favor']
        goles_contra = diccionario_estadisticas[id_equipo]['goles_en_contra']
        diccionario_estadisticas[id_equipo]['diferencia_de_goles'] = goles_favor - goles_contra

    # ==========================================
    # EL MOTOR DE DESEMPATE MATEMATICO
    # ==========================================
    def comparar_dos_equipos(estadisticas_equipo_uno, estadisticas_equipo_dos):
        # Regla 1: Quien tiene mas puntos
        if estadisticas_equipo_uno['puntos_totales'] != estadisticas_equipo_dos['puntos_totales']:
            return estadisticas_equipo_dos['puntos_totales'] - estadisticas_equipo_uno['puntos_totales']

        # Regla 2: Quien tiene mejor diferencia de goles
        if estadisticas_equipo_uno['diferencia_de_goles'] != estadisticas_equipo_dos['diferencia_de_goles']:
            return estadisticas_equipo_dos['diferencia_de_goles'] - estadisticas_equipo_uno['diferencia_de_goles']

        # Regla 3: Como salieron cuando jugaron entre ellos (Enfrentamiento Directo)
        equipo_uno = estadisticas_equipo_uno['equipo']
        equipo_dos = estadisticas_equipo_dos['equipo']

        puntos_directos_equipo_uno = 0
        puntos_directos_equipo_dos = 0

        for partido_evaluado in todos_los_partidos_jugados:
            es_cruce_directo = (partido_evaluado.equipo_local == equipo_uno and partido_evaluado.equipo_visitante == equipo_dos) or (partido_evaluado.equipo_local == equipo_dos and partido_evaluado.equipo_visitante == equipo_uno)
            
            if es_cruce_directo and "Desempate" not in partido_evaluado.fase:
                if partido_evaluado.goles_local == partido_evaluado.goles_visitante:
                    puntos_directos_equipo_uno += liga_evaluada.puntos_empate
                    puntos_directos_equipo_dos += liga_evaluada.puntos_empate
                elif partido_evaluado.goles_local > partido_evaluado.goles_visitante:
                    if partido_evaluado.equipo_local == equipo_uno:
                        puntos_directos_equipo_uno += liga_evaluada.puntos_victoria
                    else:
                        puntos_directos_equipo_dos += liga_evaluada.puntos_victoria
                else:
                    if partido_evaluado.equipo_visitante == equipo_uno:
                        puntos_directos_equipo_uno += liga_evaluada.puntos_victoria
                    else:
                        puntos_directos_equipo_dos += liga_evaluada.puntos_victoria

        if puntos_directos_equipo_uno != puntos_directos_equipo_dos:
            return puntos_directos_equipo_dos - puntos_directos_equipo_uno

        # Regla 4: Buscar si existe un Partido de Desempate jugado entre ellos
        for partido_evaluado in todos_los_partidos_jugados:
            es_cruce_directo = (partido_evaluado.equipo_local == equipo_uno and partido_evaluado.equipo_visitante == equipo_dos) or (partido_evaluado.equipo_local == equipo_dos and partido_evaluado.equipo_visitante == equipo_uno)
            
            if es_cruce_directo and "Desempate" in partido_evaluado.fase:
                # Quien gano en los 90 minutos
                if partido_evaluado.goles_local > partido_evaluado.goles_visitante:
                    return -1 if partido_evaluado.equipo_local == equipo_uno else 1
                elif partido_evaluado.goles_local < partido_evaluado.goles_visitante:
                    return -1 if partido_evaluado.equipo_visitante == equipo_uno else 1
                else:
                    # Si empataron el desempate, definen los penales
                    penales_del_local = partido_evaluado.penales_local or 0
                    penales_del_visitante = partido_evaluado.penales_visitante or 0
                    if penales_del_local > penales_del_visitante:
                        return -1 if partido_evaluado.equipo_local == equipo_uno else 1
                    elif penales_del_local < penales_del_visitante:
                        return -1 if partido_evaluado.equipo_visitante == equipo_uno else 1

        # Si llegamos a este punto, estan empatados absolutamente en todo y requieren jugar un desempate
        return 0

    # Ordenamos la lista usando nuestro motor matematico
    lista_final_estadisticas = list(diccionario_estadisticas.values())
    lista_final_estadisticas.sort(key=cmp_to_key(comparar_dos_equipos))
    
    # NUEVO: Asignamos el numero de posicion respetando los empates
    for indice_actual, fila_actual in enumerate(lista_final_estadisticas):
        if indice_actual == 0:
            fila_actual['posicion_en_tabla'] = 1
        else:
            fila_anterior = lista_final_estadisticas[indice_actual - 1]
            
            # Si la comparacion matematica dice que empatan en absolutamente todo (retorna 0)
            if comparar_dos_equipos(fila_actual, fila_anterior) == 0:
                fila_actual['posicion_en_tabla'] = fila_anterior['posicion_en_tabla']
            else:
                # Si no empatan, la posicion es su lugar real en la lista (Indice 2 = Posicion 3)
                fila_actual['posicion_en_tabla'] = indice_actual + 1
    
    return lista_final_estadisticas