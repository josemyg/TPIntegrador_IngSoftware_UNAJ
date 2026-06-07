from django import forms


from django.db.models import Subquery, OuterRef
from .models import Profesor
from .models import Cliente

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
            'certificado':forms.ClearableFileInput(attrs={'class': 'form-control','type': 'file'}),
        }

class ProfesorSinValidarForm(forms.ModelForm):
    class Meta:
        model = Profesor
        template_name = 'gestion/profesor/profesor_sinvalidar_form.html'
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
            'certificado':forms.ClearableFileInput(attrs={'class': 'form-control','type': 'file'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        template_name = 'gestion/cliente/cliente_form.html'
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
            'fechaAlta': forms.TextInput(attrs={'class':'form-control'}),
            'esSocio': forms.CheckboxInput(attrs={'class':'form-control form-check-input'}),
        }


