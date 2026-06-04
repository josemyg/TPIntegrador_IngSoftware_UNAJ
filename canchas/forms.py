from django import forms
from .models import TipoCancha

class TipoCanchaForm(forms.ModelForm):
    class Meta:
        model = TipoCancha
        fields = ['nombre', 'superficie', 'capacidad', 'precio_hora', 'estado']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-lg bg-light border-0 rounded-3 fs-6 py-2.5',
                'placeholder': 'Completar campo...'
            }),
            'superficie': forms.Select(attrs={
                'class': 'form-select form-control-lg bg-light border-0 rounded-3 fs-6 py-2.5',
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg bg-light border-0 rounded-3 fs-6 py-2.5',
                'placeholder': 'Completar campo...'
            }),
            'precio_hora': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg bg-light border-0 rounded-3 fs-6 py-2.5',
                'placeholder': 'Completar campo...',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select form-control-lg bg-light border-0 rounded-3 fs-6 py-2.5',
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