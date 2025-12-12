# empleados/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. LISTAR / ÍNDICE
    path('', views.listar_empleados, name='lista_empleados'),

    # 2. CREAR
    path('agregar/', views.agregar_empleado, name='agregar_empleado'),

    # 3. MODIFICAR
    path('editar/<int:empleado_id>/', views.editar_empleado, name='editar_empleado'),

    # 4. BORRAR
    path('borrar/<int:empleado_id>/', views.borrar_empleado, name='borrar_empleado'),
]