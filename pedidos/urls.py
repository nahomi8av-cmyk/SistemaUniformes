from django.urls import path
from . import views

# El namespace 'pedidos' ayuda a organizar las rutas si tuvieras más de una app con nombres de vista similares.
app_name = 'pedidos'

urlpatterns = [
    # 1. LISTAR: Muestra la lista de todos los pedidos
    # URL: /pedidos/listar/
    path('listar/', views.listar_pedidos, name='listar_pedidos'),

    # 2. EDITAR: Muestra el formulario y procesa la edición de un pedido específico
    # URL: /pedidos/editar/123/
    path('editar/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),

    # 3. ELIMINAR: Muestra la confirmación y procesa el borrado de un pedido específico
    # URL: /pedidos/eliminar/123/
    path('eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
]