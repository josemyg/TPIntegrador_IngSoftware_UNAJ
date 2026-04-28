from django import forms

from django.db.models import Subquery, OuterRef
from .models import Profesor

class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        template_name = 'gestion/profesor/profesor_form.html'
        fields = '__all__'
        exclude = ['estado','user_django']
        widgets = {
            'id': forms.TextInput(attrs={'class':'form-control'}),
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
            'titulo_habilitante':forms.TextInput(attrs={'class':'form-control'}),
            'institucion_habilitante':forms.TextInput(attrs={'class':'form-control'}),
            'certificado':forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }