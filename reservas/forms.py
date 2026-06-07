from datetime import datetime, timedelta, time

from django import forms

from .models import Reserva
from canchas.models import Cancha, TipoCancha


  # VALIDAR DURACIÓN MÁXIMA



# HORARIOS DISPONIBLES DEL CLUB (08:00 A 23:00)

def generar_horarios():
    horarios = []

    hora = 8
    minuto = 0

    while hora <= 23:

        horarios.append(
            (
                time(hora, minuto),
                f"{hora:02d}:{minuto:02d}"
            )
        )

        minuto += 30

        if minuto == 60:
            minuto = 0
            hora += 1

    return horarios


HORARIOS = generar_horarios()


class ReservaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Filtrar canchas para mostrar solo las activas en el formulario de reserva
        self.fields['cancha'].queryset = Cancha.objects.filter( 
            estado='DISPONIBLE'
        )

        # Establecer fecha mínima y máxima para la reserva
        hoy = datetime.now().date()
        limite = hoy + timedelta(days=6)

        self.fields['fecha'].widget.attrs.update({
            'min': hoy.strftime('%Y-%m-%d'),
            'max': limite.strftime('%Y-%m-%d')
        })

    class Meta:

        model = Reserva

        fields = [
            'cliente',
            'cancha',
            'fecha',
            'hora_inicio',
            'hora_fin'
        ]

        widgets = {

            'cliente': forms.Select(
                attrs={'class': 'form-select select2'}
            ),

            'cancha': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'hora_inicio': forms.Select(
                choices=HORARIOS,
                attrs={'class': 'form-select'}
            ),

            'hora_fin': forms.Select(
                choices=HORARIOS,
                attrs={'class': 'form-select'}
            ),
        }

    #validaciones de datosingresados por usuarios
    def clean(self):

        cleaned_data = super().clean()

        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        cancha = cleaned_data.get('cancha')

        # VALIDAR CANCHA ACTIVA

        if cancha and cancha.estado != 'DISPONIBLE':

            raise forms.ValidationError(
                'La cancha seleccionada no está disponible para reservas.'
            )

        # VALIDAR FECHA MÁXIMA
       
        if fecha:

            limite = datetime.now().date() + timedelta(days=7)

            if fecha > limite:

                raise forms.ValidationError(
                    'No se pueden realizar reservas con más de 7 días de anticipación.'
                )

    
        # VALIDACIONES DE HORARIO


        if hora_inicio and hora_fin:

            if hora_inicio < time(8, 0):

                raise forms.ValidationError(
                    'El club abre a las 08:00.'
                )

            if hora_fin > time(23, 0):

                raise forms.ValidationError(
                    'El club cierra a las 23:00.'
                )

            if hora_fin <= hora_inicio:

                raise forms.ValidationError(
                    'La hora de fin debe ser posterior a la hora de inicio.'
                )

       
            if fecha and hora_inicio and hora_fin and cancha:
            
            
                dt_inicio = datetime.combine(fecha, hora_inicio)
                dt_fin = datetime.combine(fecha, hora_fin)
            
           
                diferencia = dt_fin - dt_inicio
            
            
                horas_solicitadas = diferencia.total_seconds() / 3600
            
           
                limite_cancha = cancha.tipo.max_horas 

            
            if horas_solicitadas > limite_cancha:
                raise forms.ValidationError(
                    f"No podés reservar más de {limite_cancha} horas para este tipo de cancha (Solicitaste {horas_solicitadas:.1f} hs)."
                )
        

        # VALIDAR SUPERPOSICIÓN DE RESERVAS
      

        if fecha and hora_inicio and hora_fin and cancha:

            conflicto = Reserva.objects.filter(
                fecha=fecha,
                cancha=cancha
            ).exclude(
                estado__startswith='CANCELADA'
            )

            # Si estoy editando una reserva,
            # no debo compararla consigo misma
            if self.instance.pk:

                conflicto = conflicto.exclude(
                    pk=self.instance.pk
                )

            conflicto = conflicto.filter(
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            )

            if conflicto.exists():

                raise forms.ValidationError(
                    'Ya existe una reserva para ese horario.'
                )

        return cleaned_data