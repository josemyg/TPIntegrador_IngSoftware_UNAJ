from django.urls import path
from . import views
from reservas import views as reservas_views
from competiciones import views as competiciones_views

urlpatterns = [
    # URLs de Pagos
    path('listaPago/', views.PagoListView.as_view(), name='pago_list'),
    path('nuevoPago/', views.PagoCreateView.as_view(), name='pago_create'),
    path('pagos/<int:pk>/modificar/', views.PagoUpdateView.as_view(), name='pago_update'),
    path('pagos/<int:pk>/eliminar/', views.PagoDeleteView.as_view(), name='pago_delete'),
    path('reserva/<int:reserva_id>/pagar/',views.PagoReservaCreateView.as_view(),name='pago_create_reserva'),
    path('confirmar/<int:pk>/', views.confirmar_pago, name='confirmar_pago'),
    path('cambiar_estado/<int:pk>/', views.cambiar_estado_pago, name='cambiar_estado_pago'),
    path('pago/qr/<int:pago_id>/', views.mostrar_qr_pantalla, name='mostrar_qr_pantalla'),

    # URLs de Recibos
    path('listaRecibo/', views.ReciboListView.as_view(), name='recibo_list'),
    path('recibos/<int:pk>/modificar/', views.ReciboUpdateView.as_view(), name='recibo_update'),
    path('recibos/<int:pk>/eliminar/', views.ReciboDeleteView.as_view(), name='recibo_delete'),
    path('', reservas_views.gestion_reservas, name='lista_reservas'),
    path('recibo/descargar/<int:recibo_id>/', views.descargar_recibo_pdf, name='recibo_descargar'),
    path('recibo/enviar/<int:recibo_id>/', views.enviar_recibo_email, name='recibo_enviar'),

    path('editar/<int:id>/', reservas_views.editar_reserva, name='editar_reserva'),

    path('cancelar/<int:id>/', reservas_views.cancelar_reserva, name='cancelar_reserva'),
]