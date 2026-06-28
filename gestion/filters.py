import django_filters
from django import forms
from .models import Cliente, Profesor

class ClienteFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    apellido = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    direccion = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    localidad = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    provincia = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    pais = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    cpa = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    nacionalidad = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    telefono = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    email = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))
    dni = django_filters.CharFilter(field_name='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'apellido',
            'direccion',
            'localidad',
            'provincia',
            'pais',
            'cpa',
            'nacionalidad',
            'telefono',
            'email',
            'dni'
        ]
