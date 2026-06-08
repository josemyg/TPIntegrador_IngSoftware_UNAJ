from django import forms
from gestion.models import Cliente

class ClientePerfilForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['direccion', 'localidad', 'provincia', 'pais', 
                  'cpa', 'nacionalidad', 'telefono', 'email']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'cpa': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
        }

        