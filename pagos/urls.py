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

    # URLs de Recibos
    path('listaRecibo/', views.ReciboListView.as_view(), name='recibo_list'),
    path('recibos/<int:pk>/modificar/', views.ReciboUpdateView.as_view(), name='recibo_update'),
    path('recibos/<int:pk>/eliminar/', views.ReciboDeleteView.as_view(), name='recibo_delete'),
    path('', reservas_views.gestion_reservas, name='lista_reservas'),
    path('recibo/descargar/<int:recibo_id>/', views.descargar_recibo_pdf, name='recibo_descargar'),

    path('editar/<int:id>/', reservas_views.editar_reserva, name='editar_reserva'),

    path('cancelar/<int:id>/', reservas_views.cancelar_reserva, name='cancelar_reserva'),

    # Equipos
    path('equipos/', competiciones_views.EquipoListView.as_view(), name='equipo_list'),
    path('equipos/nuevo/', competiciones_views.EquipoCreateView.as_view(), name='equipo_create'),
    path('equipos/<int:pk>/editar/', competiciones_views.EquipoUpdateView.as_view(), name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', competiciones_views.EquipoDeleteView.as_view(), name='equipo_delete'),
    
    # Ligas
    path('ligas/', competiciones_views.LigaListView.as_view(), name='liga_list'),
    path('ligas/nueva/', competiciones_views.LigaCreateView.as_view(), name='liga_create'),
    path('ligas/editar/<int:pk>/', competiciones_views.LigaUpdateView.as_view(), name='liga_update'),
    path('ligas/eliminar/<int:pk>/', competiciones_views.LigaDeleteView.as_view(), name='liga_delete'),

    # Torneos
    path('torneos/', competiciones_views.TorneoListView.as_view(), name='torneo_list'),
    path('torneos/nuevo/', competiciones_views.TorneoCreateView.as_view(), name='torneo_create'),
    path('torneos/editar/<int:pk>/', competiciones_views.TorneoUpdateView.as_view(), name='torneo_update'),
    path('torneos/eliminar/<int:pk>/', competiciones_views.TorneoDeleteView.as_view(), name='torneo_delete'),
    # Rutas de fixture
    path('ligas/<int:pk>/', competiciones_views.LigaDetailView.as_view(), name='liga_detail'),
    path('ligas/<int:liga_id>/generar-fixture/', competiciones_views.generar_fixture_liga, name='generar_fixture_liga'),
]