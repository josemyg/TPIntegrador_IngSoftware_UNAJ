from django import forms
from .models import TipoCancha

class TipoCanchaForm(forms.ModelForm):
    class Meta:
        model = TipoCancha
        # Los campos que se van a mostrar en la web
        fields = ['nombre', 'superficie', 'capacidad']
        
        # Aquí le definimos las clases de Bootstrap y los placeholders directamente desde Python
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-lg bg-light border-0 rounded-3 fs-6',
                'placeholder': 'Ej: Fútbol 5, Fútbol 7, Básquet...'
            }),
            'superficie': forms.TextInput(attrs={
                'class': 'form-control form-control-lg bg-light border-0 rounded-3 fs-6',
                'placeholder': 'Ej: Césped Sintético, Parqué, Cemento...'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg bg-light border-0 rounded-3 fs-6',
                'placeholder': 'Ej: 10'
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