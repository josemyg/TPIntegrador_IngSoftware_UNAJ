from django import forms
from django.db.models import Subquery, OuterRef
from .models import  Descuento, TipoDescuento

class DescuentoForm(forms.ModelForm):
    class Meta:
        model=Descuento
        template_name= 'gestion/descuento/descuento_form.html'
        fields = '__all__'
        exclude = ['estado','user_django']

        widgets = {
            'tipo': forms.Select(attrs={'class':'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class':'form-control'}),
        }


class TipoDescuentoForm(forms.ModelForm):
    class Meta:
        model=TipoDescuento
        template_name='gestion/TipoDescuento/TipoDescuento_form.html'
        fields = '__all__'
        exclude = ['estado','user_django']


        widgets = {
            'nombreDescuento': forms.TextInput(attrs={'class':'form-control'}),
        }
