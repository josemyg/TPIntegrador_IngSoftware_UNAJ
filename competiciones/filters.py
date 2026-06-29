import django_filters
from django import forms
from django_filters.widgets import BooleanWidget

from gestion.models import Profesor
from .models import Equipo, Liga, Torneo, Partido, Competicion


class EquipoFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    profesor = django_filters.ModelChoiceFilter(queryset=Profesor.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Equipo
        fields = [
            'nombre',
            'profesor'
        ]

class LigaFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    estado = django_filters.ChoiceFilter(choices=Liga.estado.field.choices, widget=forms.Select(attrs={'class':'form-control'}))
    es_ida_y_vuelta = django_filters.BooleanFilter(widget=BooleanWidget(attrs={'class':'form-control'}))

    class Meta:
        model = Equipo
        fields = [
            'nombre',
            'estado',
            'es_ida_y_vuelta'
        ]

class TorneoFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    estado = django_filters.ChoiceFilter(choices=Torneo.estado.field.choices, widget=forms.Select(attrs={'class':'form-control'}))
    es_ida_y_vuelta = django_filters.BooleanFilter(widget=BooleanWidget(attrs={'class':'form-control'}))

    class Meta:
        model = Equipo
        fields = [
            'nombre',
            'estado',
            'es_ida_y_vuelta'
        ]

class PartidoFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    competicion = django_filters.ModelChoiceFilter(field_name='Tipo Competición', queryset=Competicion.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))
    equipo_local = django_filters.ModelChoiceFilter(queryset=Equipo.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))
    equipo_visitante = django_filters.ModelChoiceFilter(queryset=Equipo.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))
    jugado = django_filters.BooleanFilter(widget=BooleanWidget(attrs={'class':'form-control'}))

    class Meta:
        model = Equipo
        fields = [
            'nombre',
            'competicion',
            'equipo_local',
            'equipo_visitante',
            'jugado'
        ]