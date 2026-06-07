from django import forms
from .models import TipoCancha, Cancha

class TipoCanchaForm(forms.ModelForm):
    class Meta:
        model = TipoCancha
        fields = ['nombreTipo', 'superficie', 'capacidad', 'precio_hora', 'estado', 'max_horas']
        
        widgets = {
            'nombreTipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Completar campo...'
            }),
            'superficie': forms.Select(attrs={
                'class': 'form-control',
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Completar campo...'
            }),
            'precio_hora': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Completar campo...',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
            'max_horas': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Completar campo...'
            }),
        }

    # VOLUNTARIO: Validación personalizada (Por ejemplo, para que no pongan capacidades locas o negativas)
    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad <= 0:
            raise forms.ValidationError("La capacidad de jugadores debe ser mayor a 0.")
        if capacidad > 50:
            raise forms.ValidationError("¿Seguro? Esa capacidad parece demasiado alta para una cancha estándar.")
        return capacidad
    
    def clean_precio_hora(self):
        precio = self.cleaned_data.get('precio_hora')
        if precio < 0:
            raise forms.ValidationError("El precio por hora no puede ser un número negativo.")
        return precio
    
class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre', 'tipo', 'estado']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Completar campo...'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
        }