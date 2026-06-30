from django import forms

from django.db.models import Subquery, OuterRef
from gestion.models import Cliente
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class ClienteRegistroForm(forms.ModelForm):

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(username=email).exists():
            raise ValidationError(
                'Ya existe una cuenta registrada con este correo.'
            )
        return email

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