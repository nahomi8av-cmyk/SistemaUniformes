# escuelas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. LISTAR / BUSCAR (Página principal de la app)
    path('', views.listar_escuelas, name='lista_escuelas'),

    # 2. CREAR (Agregar nuevo registro)
    path('agregar/', views.agregar_escuela, name='agregar_escuela'),

    # 3. MODIFICAR (Editar un registro existente por ID)
    path('editar/<int:escuela_id>/', views.editar_escuela, name='editar_escuela'),

    # 4. BORRAR (Eliminar un registro por ID)
    path('borrar/<int:escuela_id>/', views.borrar_escuela, name='borrar_escuela'),
]