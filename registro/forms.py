from django import forms

from django.db.models import Subquery, OuterRef
from gestion.models import Cliente

class ClienteRegistroForm(forms.ModelForm):
    class Meta:
        model = Cliente
        template_name = 'registro/registro_cliente_form.html'
        fields = '__all__'
        exclude = ['id','fechaAlta', 'estado', 'esSocio', 'estado','user_django']

        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'apellido': forms.TextInput(attrs={'class':'form-control'}),
            'direccion': forms.TextInput(attrs={'class':'form-control'}),
            'localidad': forms.TextInput(attrs={'class':'form-control'}),
            'provincia': forms.TextInput(attrs={'class':'form-control'}),
            'pais': forms.TextInput(attrs={'class':'form-control'}),
            'cpa': forms.TextInput(attrs={'class':'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class':'form-control'}),
            'telefono': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.TextInput(attrs={'class':'form-control'}),
            'dni': forms.TextInput(attrs={'class':'form-control'}),
        }