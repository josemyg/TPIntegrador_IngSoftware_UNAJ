from django import forms
from .models import Pago
from .models import Recibo
from .models import TipoPago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        template_name = 'pagos/pago_form.html'
        fields = '__all__'
        exclude = ['estado','reserva']
        widgets = {
            'origen_pago': forms.Select(attrs={'class':'form-control'}),
            'tipo_pago': forms.Select(attrs={'class':'form-control'}),
            'monto': forms.TextInput(attrs={'class':'form-control'}),
            'fecha': forms.DateTimeInput(attrs={'class':'form-control'}),
            'descuento': forms.Select(attrs={'class':'form-control'})
        }

class ReciboForm(forms.ModelForm):
    monto_pago = forms.FloatField(
        label="Monto del Pago ($)",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    class Meta:
        model = Recibo
        fields = ['fecha'] # O los campos que estés editando del recibo
        widgets = {
            # 🟢 CLAVE: Esto transforma el input de texto aburrido en un calendario nativo
            'fecha': forms.DateInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control' # Mantiene tus estilos limpios
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pago:
            # Buscamos el monto real del pago y se lo clavamos al input
            self.fields['monto_pago'].initial = self.instance.pago.monto
