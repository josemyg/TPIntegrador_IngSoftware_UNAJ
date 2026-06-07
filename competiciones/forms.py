from django import forms
from .models import Equipo, Liga, Torneo, Partido
from canchas.models import Cancha

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        template_name = 'competiciones/equipo/equipo_form.html'
        fields = '__all__'
        labels = {
            'nombre': 'Nombre del Equipo',
            'profesor': 'Profesor Asignado',
            'clientes': 'Integrantes (Maximo 15)'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'profesor': forms.Select(attrs={'class': 'form-control'}),
            'clientes': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}), 
        }

        def clean_clientes(self):
            clientes = self.cleaned_data.get('clientes')
            if len(clientes) > 5:
                raise forms.ValidationError("No se pueden seleccionar mas de 5 clientes.")
            return clientes

class LigaForm(forms.ModelForm):
    class Meta:
        model = Liga
        fields = ['nombre', 'estado', 'equipos', 'puntos_victoria', 'puntos_empate']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Superliga 2026'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'equipos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'puntos_victoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'puntos_empate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TorneoForm(forms.ModelForm):
    class Meta:
        model = Torneo
        fields = ['nombre', 'estado', 'equipos', 'es_ida_y_vuelta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Copa Argentina'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'equipos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'es_ida_y_vuelta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
class AsignarCanchaForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['cancha_asignada', 'fecha_y_hora_encuentro']
        widgets = {
            'fecha_y_hora_encuentro': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'cancha_asignada': forms.Select(attrs={'class': 'form-select'})
        }

    def clean(self):
        datos_limpios = super().clean()
        cancha_seleccionada = datos_limpios.get('cancha_asignada')
        fecha_seleccionada = datos_limpios.get('fecha_y_hora_encuentro')

        if cancha_seleccionada and fecha_seleccionada:
            # Buscamos si existe algun otro partido en esa misma cancha y hora exacta
            partido_existente = Partido.objects.filter(
                cancha_asignada=cancha_seleccionada,
                fecha_y_hora_encuentro=fecha_seleccionada
            ).exclude(id=self.instance.id).exists()

            if partido_existente:
                raise forms.ValidationError("Error: La cancha seleccionada ya esta reservada para otro partido en ese mismo horario.")

        return datos_limpios