from django import forms
from .models import Clase, Entrenamiento
from gestion.models import Cliente, Profesor
from django.core.exceptions import ValidationError
from django.utils import timezone
from canchas.models import Cancha


class ClaseForm(forms.ModelForm):
    

    class Meta:
        model = Clase
        fields = ['nombre','profesor', 'alumnos','reserva', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'profesor': forms.Select(attrs={'class': 'form-control'}),
            'alumnos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'reserva': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        alumnos = cleaned.get('alumnos')
        cupo = cleaned.get('cupo_maximo')

        if alumnos is not None and cupo is not None and len(alumnos) > cupo:
            raise ValidationError(
                'No puede seleccionar más alumnos que el cupo máximo.')

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profesor'].queryset = Profesor.objects.filter(estado = 'activo')
        if not self.instance.pk:
            self.fields.pop('estado')
        
        


class EntrenamientoForm(forms.ModelForm):
    


    class Meta:
        model = Entrenamiento
        fields = ['nombre','entrenador', 'alumnos','reserva', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'entrenador': forms.Select(attrs={'class': 'form-control'}),
            'alumnos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'reserva': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        alumnos = cleaned.get('alumnos')
        cupo = cleaned.get('cupo_maximo')

        if alumnos is not None and cupo is not None and len(alumnos) > cupo:
            raise ValidationError(
                'No puede seleccionar más alumnos que el cupo máximo.')
        
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entrenador'].queryset = Profesor.objects.filter(estado = 'activo')
        if not self.instance.pk:
            self.fields.pop('estado')
        



