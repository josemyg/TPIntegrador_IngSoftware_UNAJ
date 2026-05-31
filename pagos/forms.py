from django import forms
from .models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['tipo_pago', 'descuento']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Recorremos los campos para clavarles la clase limpia de tu style.css
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control form-custom-input'})
        
        # Ajustes específicos para los selectores
        self.fields['tipo_pago'].empty_label = "Seleccione el método de pago..."
        self.fields['descuento'].empty_label = "Sin descuento aplicado"