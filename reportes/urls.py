from django.urls import path
from . import views

urlpatterns = [
    path('ingresos/', views.reporte_ingresos, name='reporte_ingresos'),
    path("ingresos/pdf/",views.exportar_pdf,name="exportar_pdf")
]