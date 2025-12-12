from django.urls import path
from . import views

urlpatterns = [
    # Corresponde a la tarjeta "Nuevo Pedido" y al menú "Venta"
    # URL: /ventas/nuevo/
    path('nuevo/', views.nueva_venta, name='nueva_venta'),

    # Corresponde a la tarjeta "Nuevo Pago" y al menú "Pago"
    # URL: /ventas/pago/
    path('pago/', views.nuevo_pago, name='nuevo_pago'),
    path('pedidos/detalle/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),

]