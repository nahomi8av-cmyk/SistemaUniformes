# pagos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Pantalla de búsqueda de pedidos
    path('buscar/', views.buscar_pedido, name='buscar_pedido_pago'),

    # 2. Pantalla para registrar el pago (acepta el ID del pedido)
    path('registrar/<int:pedido_id>/', views.registrar_pago, name='registrar_pago'),

    # 1. LISTAR: Muestra la lista de todos los pagos
    path('listar/', views.listar_pagos, name='listar_pagos'),

    # 2. EDITAR: Muestra el formulario y procesa la edición de un pago específico
    path('editar/<int:pago_id>/', views.editar_pago, name='editar_pago'),

    # 3. ELIMINAR: Muestra la confirmación y procesa el borrado de un pago específico
    path('eliminar/<int:pago_id>/', views.eliminar_pago, name='eliminar_pago'),
]