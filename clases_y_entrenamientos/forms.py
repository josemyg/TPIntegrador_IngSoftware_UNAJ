from django import forms
from .models import Clase, Entrenamiento
from gestion.models import Cliente
from django.core.exceptions import ValidationError
from django.utils import timezone


class ClaseForm(forms.ModelForm):
    horario = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    def clean_horario(self):
        horario = self.cleaned_data.get('horario')
        if horario and horario < timezone.now():
            raise forms.ValidationError(
                'La fecha y hora seleccionas no son válidas.')
        return horario

    class Meta:
        model = Clase
        fields = ['nombre', 'horario', 'cupo_maximo',
                  'profesor', 'alumnos', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cupo_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'profesor': forms.Select(attrs={'class': 'form-control'}),
            'alumnos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        alumnos = cleaned.get('alumnos')
        cupo = cleaned.get('cupo_maximo')

        if alumnos is not None and cupo is not None and len(alumnos) > cupo:
            raise ValidationError(
                'No puede seleccionar más alumnos que el cupo máximo.')

        if self.instance.pk:  # solo al editar, no al crear
            estado_actual = self.instance.estado
            estado_nuevo = cleaned.get('estado')
            if estado_actual != estado_nuevo:
                transiciones_validas = {
                    'programada': ['en_curso', 'cancelada'],
                    'en_curso': ['finalizada', 'cancelada'],
                    'finalizada': [],
                    'cancelada': [],
                }
                if estado_nuevo not in transiciones_validas.get(estado_actual, []):
                    raise ValidationError(
                        f'No se puede cambiar el estado de "{estado_actual}" a "{estado_nuevo}".')

        return cleaned


class EntrenamientoForm(forms.ModelForm):
    horario = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    def clean_horario(self):
        horario = self.cleaned_data.get('horario')
        if horario and horario < timezone.now():
            raise forms.ValidationError(
                'La fecha y hora seleccionas no son válidas.')
        return horario

    class Meta:
        model = Entrenamiento
        fields = ['nombre', 'horario', 'cupo_maximo',
                  'entrenador', 'alumnos', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cupo_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'entrenador': forms.Select(attrs={'class': 'form-control'}),
            'alumnos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        alumnos = cleaned.get('alumnos')
        cupo = cleaned.get('cupo_maximo')

        if alumnos is not None and cupo is not None and len(alumnos) > cupo:
            raise ValidationError(
                'No puede seleccionar más alumnos que el cupo máximo.')
        if self.instance.pk:  # solo al editar, no al crear
            estado_actual = self.instance.estado
            estado_nuevo = cleaned.get('estado')
            if estado_actual != estado_nuevo:
                transiciones_validas = {
                    'programada': ['en_curso', 'cancelada'],
                    'en_curso': ['finalizada', 'cancelada'],
                    'finalizada': [],
                    'cancelada': [],
                }
                if estado_nuevo not in transiciones_validas.get(estado_actual, []):
                    raise ValidationError(
                        f'No se puede cambiar el estado de "{estado_actual}" a "{estado_nuevo}".')

        return cleaned
