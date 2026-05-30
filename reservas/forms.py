# reservas/forms.py
from datetime import datetime, timedelta
from django import forms
from .models import Reserva
from canchas.models import TipoCancha

class ReservaForm(forms.ModelForm): # crea un formulario basado en el modelo Reserva

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tipo_cancha'].queryset = TipoCancha.objects.filter(
        estado='activo'
        ) # Filtra el queryset del campo tipo_cancha para mostrar solo las canchas que están activas. Esto se hace en el método __init__ del formulario, lo que permite personalizar el comportamiento del formulario al momento de su creación.
    class Meta:
        model = Reserva
        fields = [
            'cliente',
            'tipo_cancha',
            'fecha',
            'hora_inicio',
            'hora_fin'
        ]
        widgets = {
            'cliente': forms.Select(
                attrs={'class': 'form-select select2'}
            ),
            'tipo_cancha': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'fecha': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'hora_inicio': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
            'hora_fin': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean() # llama al método de limpieza del formulario para obtener los datos limpios y realizar validaciones personalizadas.

        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        tipo_cancha = cleaned_data.get('tipo_cancha')

        if tipo_cancha and tipo_cancha.estado != 'activo':
            raise forms.ValidationError(
                'La cancha seleccionada no está disponible para reservas.'
            ) # Si se ha seleccionado un tipo de cancha y su estado no es 'activo', se lanza una validación de error indicando que la cancha seleccionada no está disponible para reservas.
        if fecha:
            limite = datetime.now().date() + timedelta(days=7)
            if fecha > limite:
            # Si la fecha de reserva es mayor a 7 días a partir de hoy, se lanza una validación de error.
                raise forms.ValidationError(
                    'No se pueden realizar reservas con más de 7 días de anticipación'
                ) 
        
        if hora_inicio and hora_fin and tipo_cancha: # Si se han proporcionado la hora de inicio, la hora de fin y el tipo de cancha, se realiza la validación de duración.
            inicio = datetime.combine(datetime.today(), hora_inicio) # Combina la fecha actual con la hora de inicio para crear un objeto datetime completo.
            fin = datetime.combine(datetime.today(), hora_fin) # Combina la fecha actual con la hora de fin para crear un objeto datetime completo.
            duracion = fin - inicio # Calcula la duración de la reserva restando la hora de inicio de la hora de fin.

            limites = {
                'Futbol 5': timedelta(hours=1),
                'Futbol 7': timedelta(hours=2),
                'Futbol 11': timedelta(hours=2),
            } # Define un diccionario que establece los límites de duración para cada tipo de cancha. Las claves son los tipos de cancha y los valores son objetos timedelta que representan la duración máxima permitida para cada tipo de cancha.

            max_duracion = limites.get(tipo_cancha.nombre) # Obtiene el límite de duración correspondiente al tipo de cancha seleccionado utilizando el nombre del tipo de cancha como clave en el diccionario limites.
            if max_duracion and duracion > max_duracion:
                raise forms.ValidationError(
                    f'La duración máxima para {tipo_cancha.nombre} es {max_duracion}.'
                ) # Si la duración de la reserva excede el límite permitido para el tipo de cancha seleccionado, se lanza una validación de error con un mensaje que indica la duración máxima permitida para ese tipo de cancha.

        return cleaned_data

