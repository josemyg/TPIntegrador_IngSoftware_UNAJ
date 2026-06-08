from django import forms
from gestion.models import Cliente
from reservas.models import Reserva

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

 

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cancha', 'fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'cancha': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'cancha': 'Cancha',
            'fecha': 'Fecha de la reserva',
            'hora_inicio': 'Hora de inicio',
            'hora_fin': 'Hora de fin',
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        cancha = cleaned_data.get('cancha')
        if fecha and hora_inicio and hora_fin and cancha:
            if hora_inicio >= hora_fin:
                raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            duracion = (hora_fin.hour - hora_inicio.hour) + (hora_fin.minute - hora_inicio.minute) / 60
            if duracion > cancha.tipo.max_horas:
                raise forms.ValidationError(f"No se puede reservar más de {cancha.tipo.max_horas} horas para este tipo de cancha.")
        return cleaned_data   