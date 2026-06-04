from django.contrib import admin
from .models import TipoPago, Pago, Recibo

admin.site.register(TipoPago)
admin.site.register(Pago)
admin.site.register(Recibo)
