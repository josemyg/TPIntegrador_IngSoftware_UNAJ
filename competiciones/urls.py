from django.urls import path
from . import views

urlpatterns = [
    
    #Equipos
	path('equipos/', views.EquipoListView.as_view(), name='equipo_list'),
	path('equipos/nuevo/', views.EquipoCreateView.as_view(), name='equipo_create'),
	path('equipos/<int:pk>/editar/', views.EquipoUpdateView.as_view(), name='equipo_update'),
	path('equipos/<int:pk>/eliminar/', views.EquipoDeleteView.as_view(), name='equipo_delete'),
    
    #Ligas
    path('ligas/', views.LigaListView.as_view(), name='liga_list'),
    path('ligas/nueva/', views.LigaCreateView.as_view(), name='liga_create'),
    path('ligas/editar/<int:pk>/', views.LigaUpdateView.as_view(), name='liga_update'),
    path('ligas/eliminar/<int:pk>/', views.LigaDeleteView.as_view(), name='liga_delete'),

    #Torneos
    path('torneos/', views.TorneoListView.as_view(), name='torneo_list'),
    path('torneos/nuevo/', views.TorneoCreateView.as_view(), name='torneo_create'),
    path('torneos/editar/<int:pk>/', views.TorneoUpdateView.as_view(), name='torneo_update'),
    path('torneos/eliminar/<int:pk>/', views.TorneoDeleteView.as_view(), name='torneo_delete'),
    # Rutas para Ligas
    path('ligas/', views.LigaListView.as_view(), name='liga_list'),
    path('ligas/nueva/', views.LigaCreateView.as_view(), name='liga_create'),
    path('ligas/editar/<int:pk>/', views.LigaUpdateView.as_view(), name='liga_update'),
    path('ligas/eliminar/<int:pk>/', views.LigaDeleteView.as_view(), name='liga_delete'),
    
    # rUTAS DE FIXTURE
    path('ligas/<int:pk>/', views.LigaDetailView.as_view(), name='liga_detail'),
    path('ligas/<int:pk>/generar-fixture/', views.generar_fixture_liga, name='generar_fixture_liga'),
]