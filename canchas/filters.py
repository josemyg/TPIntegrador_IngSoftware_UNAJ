import django_filters
from django import forms
from django_filters.widgets import BooleanWidget

from .models import Cancha, TipoCancha


class CanchaFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    tipo = django_filters.ModelChoiceFilter(queryset=TipoCancha.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))
    estado = django_filters.ChoiceFilter(choices=Cancha.estado.field.choices, widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Cancha
        fields = [
            'nombre',
            'tipo',
            'estado'
        ]

class TipoCanchaFilter(django_filters.FilterSet):

    nombreTipo = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    capacidad = django_filters.NumberFilter(lookup_expr='exact', widget=forms.TextInput(attrs={'class':'form-control'}))
    superficie = django_filters.ChoiceFilter(choices=TipoCancha.estado.field.choices, widget=forms.Select(attrs={'class':'form-control'}))
    estado = django_filters.ChoiceFilter(choices=Cancha.estado.field.choices, widget=forms.Select(attrs={'class':'form-control'}))
    max_horas = django_filters.NumberFilter(lookup_expr='exact', widget=forms.TextInput(attrs={'class':'form-control'}))
    mayor_max_horas = django_filters.NumberFilter(field_name='Horas máx mayores a', lookup_expr='gte', widget=forms.TextInput(attrs={'class':'form-control'}))
    menor_max_horas = django_filters.NumberFilter(field_name='Horas máx menores a', lookup_expr='lte', widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = TipoCancha
        fields = [
            'nombreTipo',
            'capacidad',
            'superficie',
            'estado',
            'max_horas',
            'mayor_max_horas',
            'menor_max_horas'
        ]
