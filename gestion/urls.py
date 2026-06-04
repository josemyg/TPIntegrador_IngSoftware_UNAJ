from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from .views import *

urlpatterns = [
    path('', views.inicio, name = 'inicio'),
    path('listaprofesores', ProfesorListView.as_view(), name = 'profesor_list'),
    path("crearprofesor", ProfesorCreateView.as_view(), name="profesor_create"),
    path("modificarprofesor/<pk>", ProfesorUpdateView.as_view(), name="profesor_update"), 
    path("eliminarprofesor/<pk>", ProfesorDeleteView.as_view(), name="profesor_delete"),
    path("modificarprofesor/<pk>", ProfesorUpdateView.as_view(), name="profesor_update"),
    path("imprimirprofesor/<pk>", ProfesorPrintView.as_view(), name="profesor_print"),
    path('verificarprofesor/<int:pk>/',ProfesorVerificar,name='profesor_verificar'),


    # CLIENTE
    path('listaclientes', ClienteListView.as_view(), name='cliente_list'),
    path('crearcliente', ClienteCreateView.as_view(), name='cliente_create'),
    path('eliminarcliente/<pk>', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('modificarcliente/<pk>', ClienteUpdateView.as_view(), name='cliente_update'),
    path("imprimircliente/<pk>", ClientePrintView.as_view(), name="cliente_print"),




]   
