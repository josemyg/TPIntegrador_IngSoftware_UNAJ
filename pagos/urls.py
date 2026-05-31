from django.urls import path
from . import views

urlpatterns = [
    # URLs de Pagos
    path('listaPago/', views.PagoListView.as_view(), name='pago_list'),
    path('nuevoPago/', views.PagoCreateView.as_view(), name='pago_create'),
    path('pagos/<int:pk>/modificar/', views.PagoUpdateView.as_view(), name='pago_update'),
    path('pagos/<int:pk>/eliminar/', views.PagoDeleteView.as_view(), name='pago_delete'),
    path('reserva/<int:reserva_id>/pagar/',views.PagoReservaCreateView.as_view(),name='pago_create_reserva'),

    # URLs de Recibos
    path('listaRecibo/', views.ReciboListView.as_view(), name='recibo_list'),
    path('recibos/<int:pk>/modificar/', views.ReciboUpdateView.as_view(), name='recibo_update'),
    path('recibos/<int:pk>/eliminar/', views.ReciboDeleteView.as_view(), name='recibo_delete'),
    path('recibos/<int:pk>/imprimir/', views.ReciboImprimirView.as_view(), name='recibo_imprimir'),
]