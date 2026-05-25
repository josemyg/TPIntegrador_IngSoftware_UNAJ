from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from .views import *

urlpatterns = [
    path('', views.inicio, name = 'inicio'),
    path('listaprofesores', ProfesorListView.as_view(), name = 'profesor_list'),
    path("crearprofesor", ProfesorCreateView.as_view(), name="profesor_create"),
    path("eliminarprofesor/<pk>", ProfesorDeleteView.as_view(), name="profesor_delete"),
    path("modificarprofesor/<pk>", ProfesorUpdateView.as_view(), name="profesor_update"),   
]