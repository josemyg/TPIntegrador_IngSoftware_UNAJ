import django_filters
from django import forms
from django_filters.widgets import BooleanWidget

from gestion.models import Profesor
from canchas.models import Cancha
from reservas.models import Reserva
from .models import Clase, Entrenamiento

class ClaseFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    horario = django_filters.DateTimeFilter(lookup_expr='icontains', widget=forms.DateTimeInput(attrs={'class':'form-control'}))
    cupo_maximo = django_filters.NumberFilter(lookup_expr='icontains', widget=forms.NumberInput(attrs={'class':'form-control'}))
    profesor = django_filters.ModelChoiceFilter(queryset=Profesor.objects.all(), lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    cancha = django_filters.ModelChoiceFilter(queryset=Cancha.objects.all(), lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    reserva = django_filters.ModelChoiceFilter(queryset=Reserva.objects.all(), lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    estado = django_filters.ChoiceFilter(choices=Clase.ESTADO_OPCIONES , widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Clase
        fields = [
            'nombre',
            'horario',
            'cupo_maximo',
            'profesor',
            'cancha',
            'reserva',
            'estado'
        ]

class EntrenamientoFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    horario = django_filters.DateTimeFilter(lookup_expr='icontains', widget=forms.DateTimeInput(attrs={'class':'form-control'}))
    cupo_maximo = django_filters.NumberFilter(lookup_expr='icontains', widget=forms.NumberInput(attrs={'class':'form-control'}))
    profesor = django_filters.ModelChoiceFilter(queryset=Profesor.objects.all(), lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    cancha = django_filters.ModelChoiceFilter(queryset=Cancha.objects.all(), lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    reserva = django_filters.ModelChoiceFilter(queryset=Reserva.objects.all(), lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    estado = django_filters.ChoiceFilter(choices=Entrenamiento.ESTADO_OPCIONES , widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Entrenamiento
        fields = [
            'nombre',
            'horario',
            'cupo_maximo',
            'profesor',
            'cancha',
            'reserva',
            'estado'
        ]