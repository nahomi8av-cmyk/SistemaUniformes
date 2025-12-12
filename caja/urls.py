# caja/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('abrir/', views.abrir_caja, name='abrir_caja'),
    path('cerrar/', views.cerrar_caja, name='cerrar_caja'),

    # 1. LISTAR: Muestra la lista de todas las sesiones
    path('listar/', views.listar_sesiones, name='listar_sesiones'),

    # 2. EDITAR: Muestra el formulario y procesa la edición de una sesión específica
    path('editar/<int:sesion_id>/', views.editar_sesion, name='editar_sesion'),

    # 3. ELIMINAR: Muestra la confirmación y procesa el borrado de una sesión específica
    path('eliminar/<int:sesion_id>/', views.eliminar_sesion, name='eliminar_sesion'),

# Nuevas Rutas para Movimientos de Caja
    path('movimientos/', views.listar_movimientos, name='listar_movimientos'),
    path('movimientos/agregar/', views.agregar_movimiento, name='agregar_movimiento'),
    path('movimientos/editar/<int:movimiento_id>/', views.editar_movimiento, name='editar_movimiento'),
    path('movimientos/borrar/<int:movimiento_id>/', views.borrar_movimiento, name='borrar_movimiento'),

]