from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'clases_y_entrenamientos'

urlpatterns = [
   # RUTAS DE CLASES
    path('clase/', views.ClaseListView.as_view(), name='clase_list'),
    path('clase/crear/', views.ClaseCreateView.as_view(), name='clase_create'),
    path('clase/<int:pk>/editar/', views.ClaseUpdateView.as_view(), name='clase_update'),
    path('clase/<int:pk>/eliminar/', views.ClaseDeleteView.as_view(), name='clase_delete'),
    path('clase/<int:pk>/imprimir/', views.ClasePrintView.as_view(), name='clase_print'),
    path('clase/<int:pk>/tomar-asistencia/', views.tomar_asistencia_clase, name='tomar_asistencia_clase'),
    path('clase/<int:pk>/reporte/', views.ClaseReporteView.as_view(), name='clase_reporte'),
    path('clase/<int:pk>/reporte/pdf/', views.reporte_clase_pdf, name='clase_reporte_pdf'),


     # RUTAS DE ENTRENAMIENTOS
    path('entrenamiento/', views.EntrenamientoListView.as_view(), name='entrenamiento_list'),
    path('entrenamiento/crear/', views.EntrenamientoCreateView.as_view(), name='entrenamiento_create'),
    path('entrenamiento/<int:pk>/editar/', views.EntrenamientoUpdateView.as_view(), name='entrenamiento_update'),
    path('entrenamiento/<int:pk>/eliminar/', views.EntrenamientoDeleteView.as_view(), name='entrenamiento_delete'),
    path('entrenamiento/<int:pk>/imprimir/', views.EntrenamientoPrintView.as_view(), name='entrenamiento_print'),
    path('entrenamiento/<int:pk>/tomar-asistencia/', views.tomar_asistencia_entrenamiento, name='tomar_asistencia_entrenamiento'),
    path('entrenamiento/<int:pk>/reporte/', views.EntrenamientoReporteView.as_view(), name='entrenamiento_reporte'),
    path('entrenamiento/<int:pk>/reporte/pdf/', views.reporte_entrenamiento_pdf, name='entrenamiento_reporte_pdf'),
]