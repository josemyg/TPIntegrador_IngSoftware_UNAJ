from datetime import datetime, timedelta, time
from django import forms
from .models import Reserva
from canchas.models import Cancha, TipoCancha

def generar_horarios():
    horarios = []
    hora = 8
   
    while hora <= 23:
        horarios.append((time(hora, 0), f"{hora:02d}:00"))
        hora += 1
    return horarios

HORARIOS = generar_horarios()

class ReservaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cancha'].queryset = Cancha.objects.filter(estado='DISPONIBLE')

        # Establecer fecha mínima y máxima para la reserva
        hoy = datetime.now().date()
        limite = hoy + timedelta(days=7)

        self.fields['fecha'].widget.attrs.update({
            'min': hoy.strftime('%Y-%m-%d'),
            'max': limite.strftime('%Y-%m-%d')
        })

    class Meta:
        model = Reserva
        fields = ['cliente', 'cancha', 'fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select select2'}),
            'cancha': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.Select(choices=HORARIOS, attrs={'class': 'form-select'}),
            'hora_fin': forms.Select(choices=HORARIOS, attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        cancha = cleaned_data.get('cancha')

        
        if cancha and cancha.estado != 'DISPONIBLE':
            raise forms.ValidationError(
                'La cancha seleccionada no está disponible para reservas.'
            )

        # 2. VALIDAR FECHA MÁXIMA
        if fecha:
            limite = datetime.now().date() + timedelta(days=7)
            if fecha > limite:
                raise forms.ValidationError(
                    'No se pueden realizar reservas con más de 7 días de anticipación.'
                )

        # 3. VALIDACIONES BÁSICAS DE HORARIO
        if hora_inicio and hora_fin:
            if hora_inicio < time(8, 0):
                raise forms.ValidationError('El club abre a las 08:00.')

            if hora_fin > time(23, 0):
                raise forms.ValidationError('El club cierra a las 23:00.')

            if hora_fin <= hora_inicio:
                raise forms.ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

        # 4. VALIDAR DURACIÓN MÁXIMA POR CANCHA (¡FUNCIONANDO!)
        if fecha and hora_inicio and hora_fin and cancha:
            dt_inicio = datetime.combine(fecha, hora_inicio)
            dt_fin = datetime.combine(fecha, hora_fin)
            
            diferencia = dt_fin - dt_inicio
            horas_solicitadas = diferencia.total_seconds() / 3600.0

            limite_cancha = float(cancha.tipo.max_horas) 

            if horas_solicitadas > limite_cancha:
                raise forms.ValidationError({
                    'hora_fin': f"No podés reservar más de {int(limite_cancha)} horas seguidas para esta cancha (Solicitaste {horas_solicitadas:.1f} hs)."
                })

        # 5. VALIDAR SUPERPOSICIÓN DE RESERVAS
        if fecha and hora_inicio and hora_fin and cancha:
            conflicto = Reserva.objects.filter(
                fecha=fecha,
                cancha=cancha
            ).exclude(
                estado__icontains='cancelada'
            )

            # Si estoy editando una reserva, no la comparo consigo misma
            if self.instance and self.instance.pk:
                conflicto = conflicto.exclude(pk=self.instance.pk)

            conflicto = conflicto.filter(
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            )

            if conflicto.exists():
                raise forms.ValidationError({
                    'hora_inicio': 'Ya existe una reserva activa para esa cancha en el horario seleccionado.'
                })

        return cleaned_data