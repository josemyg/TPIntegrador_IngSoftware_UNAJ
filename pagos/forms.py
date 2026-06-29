from django import forms
from .models import Pago
from .models import Recibo
from .models import TipoPago
from descuentos.models import Descuento

class PagoForm(forms.ModelForm):
    # 1. Declaramos los campos virtuales que pide la interfaz (no obligatorios por defecto)
    comprobante_archivo = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'id': 'comprobanteFile'})
    )
    tarjeta_ultimos_4 = forms.CharField(
        max_length=4, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 4542', 'id': 'tarjeta4', 'maxlength': '4'})
    )
    tarjeta_cupon = forms.CharField(
        max_length=6, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0124', 'id': 'tarjetaCupon', 'maxlength': '6'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 2. Aprovechamos para filtrar solo los descuentos que estén activos (lo que vimos antes)
        if 'descuento' in self.fields:
            Descuento = self.fields['descuento'].queryset.model # Por si cambia la importación
            self.fields['descuento'].queryset = Descuento.objects.filter(estado='activo')
            self.fields['descuento'].empty_label = "Sin descuento (Tarifa estándar)"

    class Meta:
        model = Pago
        template_name = 'pagos/pago_form.html'
        fields = '__all__'
        exclude = ['estado', 'reserva']
        widgets = {
            'origen_pago': forms.Select(attrs={'class': 'form-control'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'descuento': forms.Select(attrs={'class': 'form-control'})
        }

    # 3. Validaciones cruzadas en el Servidor
    def clean(self):
        cleaned_data = super().clean()
        tipo_pago = cleaned_data.get('tipo_pago')

        if tipo_pago:
            # Pasamos a minúsculas el nombre del tipo de pago para que la validación sea flexible
            nombre_tipo = tipo_pago.nombre.lower()

            # SI SE ELIGIÓ TRANSFERENCIA
            if 'transferencia' in nombre_tipo:
                # Revisamos si subieron el archivo a través de request.FILES
                comprobante = self.files.get('comprobante_archivo') or cleaned_data.get('comprobante_archivo')
                if not comprobante:
                    raise forms.ValidationError(
                        'Operación bloqueada en servidor: Es obligatorio adjuntar el archivo digital del comprobante bancario.'
                    )

            # SI SE ELIGIÓ TARJETA (Débito o Crédito)
            elif 'tarjeta' in nombre_tipo or 'débito' in nombre_tipo or 'debito' in nombre_tipo:
                u4 = cleaned_data.get('tarjeta_ultimos_4')
                cupon = cleaned_data.get('tarjeta_cupon')
                
                if not u4 or len(u4) < 4:
                    raise forms.ValidationError(
                        'Operación bloqueada en servidor: Debe ingresar los últimos 4 dígitos del plástico de la tarjeta.'
                    )
                if not cupon:
                    raise forms.ValidationError(
                        'Operación bloqueada en servidor: Debe especificar el número de cupón emitido por el Posnet.'
                    )

        return cleaned_data

class ReciboForm(forms.ModelForm):
    monto_pago = forms.FloatField(
        label="Monto del Pago ($)",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    class Meta:
        model = Recibo
        fields = []  # fecha se genera automáticamente con auto_now_add=True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pago:
            # Buscamos el monto real del pago y se lo clavamos al input
            self.fields['monto_pago'].initial = self.instance.pago.monto
