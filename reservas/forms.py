from datetime import datetime, timedelta, time

from django import forms

from .models import Reserva
from canchas.models import TipoCancha



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
        self.fields['tipo_cancha'].queryset = TipoCancha.objects.filter(
            estado='activo'
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
        tipo_cancha = cleaned_data.get('tipo_cancha')

        # VALIDAR CANCHA ACTIVA

        if tipo_cancha and tipo_cancha.estado != 'activo':

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

        # VALIDAR DURACIÓN MÁXIMA

        if hora_inicio and hora_fin and tipo_cancha:

            inicio = datetime.combine(
                datetime.today(),
                hora_inicio
            )

            fin = datetime.combine(
                datetime.today(),
                hora_fin
            )

            duracion = fin - inicio

            limites = {

                'Futbol 5': timedelta(hours=1),

                'Futbol 7': timedelta(hours=2),

                'Futbol 11': timedelta(hours=2),
            }

            max_duracion = limites.get(
                tipo_cancha.nombre
            )

            if max_duracion and duracion > max_duracion:

                raise forms.ValidationError(
                    f'La duración máxima para {tipo_cancha.nombre} es {max_duracion}.'
                )

        # VALIDAR SUPERPOSICIÓN DE RESERVAS
      

        if fecha and hora_inicio and hora_fin and tipo_cancha:

            conflicto = Reserva.objects.filter(
                fecha=fecha,
                tipo_cancha=tipo_cancha
            ).exclude(
                estado='CANCELADA'
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