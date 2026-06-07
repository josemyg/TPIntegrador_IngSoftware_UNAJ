from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import *



urlpatterns = [
    path('', login_required(views.inicio), name = 'inicio'),
    path('listaprofesores', ProfesorListView.as_view(), name = 'profesor_list'),
    path('listaprofesoresaverificar', ProfesoresaValidarListView.as_view(), name = 'profesoresavalidar_list'),
    path("crearprofesor", ProfesorCreateView.as_view(), name="profesor_create"),
    path("modificarprofesor/<pk>", ProfesorUpdateView.as_view(), name="profesor_update"),
    path("modificarprofesorsinvalidar/<pk>", ProfesorAVerificarUpdateView.as_view(), name="profesoraverificar_update"),
    path("eliminarprofesor/<pk>", ProfesorDeleteView.as_view(), name="profesor_delete"),
    path("modificarprofesor/<pk>", ProfesorUpdateView.as_view(), name="profesor_update"),
    path("imprimirprofesor/<pk>", ProfesorPrintView.as_view(), name="profesor_print"),
    path('verificarprofesor/<int:pk>/',ProfesorVerificarView.as_view(),name='profesor_verificar'),
    path('confirmarverificacionprofesor/<int:pk>/',views.ConfirmarVerificacionProfesor,name='profesor_confrimarverificacion'),


    # CLIENTE
    path('listaclientes', ClienteListView.as_view(), name='cliente_list'),
    path('crearcliente', ClienteCreateView.as_view(), name='cliente_create'),
    path('eliminarcliente/<pk>', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('modificarcliente/<pk>', ClienteUpdateView.as_view(), name='cliente_update'),
    path("imprimircliente/<pk>", ClientePrintView.as_view(), name="cliente_print"),


    # VistaCliente
    path('inicio/', views.inicio, name='inicio'),
]   