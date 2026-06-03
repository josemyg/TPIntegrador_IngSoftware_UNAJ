from django import forms
from .models import Equipo, Liga, Torneo

class EquipoForm(forms.ModelForm):
	class Meta:
		model = Equipo
		template_name = 'competiciones/equipo/equipo_form.html'
		fields = '__all__'
		widgets = {
			'nombre': forms.TextInput(attrs={'class':'form-control'}),
			'profesor': forms.Select(attrs={'class': 'form-select'}),
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
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'equipos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'puntos_victoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'puntos_empate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TorneoForm(forms.ModelForm):
    class Meta:
        model = Torneo
        fields = ['nombre', 'estado', 'equipos', 'es_ida_y_vuelta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Copa del Rey'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'equipos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'es_ida_y_vuelta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }