# clientes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. BÚSQUEDA Y PERFIL (Rutas existentes)
    path('buscar/', views.buscar_cliente, name='buscar_cliente'),
    path('<int:cliente_id>/perfil/', views.perfil_cliente, name='perfil_cliente'),

    # 💥 RUTA RAÍZ: LISTAR (Apunta a la nueva función listar_clientes) 💥
    path('', views.listar_clientes, name='lista_clientes'),

    # 💥 RUTAS CRUD FALTANTES 💥
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    # Nota: La vista borrar_cliente renderiza tu plantilla renombrada 'confirmar_borrar.html'
    path('borrar/<int:cliente_id>/', views.borrar_cliente, name='borrar_cliente'),
]