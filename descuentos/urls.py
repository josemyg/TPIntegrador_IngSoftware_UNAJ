from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.DescuentoListView.as_view(), name='descuento_list'),
    path('create/', views.DescuentoCreateView.as_view(), name='descuento_create'),
    path('update/<pk>/', views.DescuentoUpdateView.as_view(), name='descuento_update'),
    path('delete/<pk>/', views.DescuentoDeleteView.as_view(), name='descuento_delete'),
    path('print/<pk>/', views.DescuentoPrintView.as_view(), name='descuento_print'),
    path('baja/<pk>/', views.DescuentoBaja, name='descuento_verificar'),
]