from django.urls import path
from . import views

urlpatterns = [
    # 1. RUTA PRINCIPAL (Nueva): Muestra la lista de escuelas para seleccionar.
    path('', views.seleccionar_escuela, name='seleccionar_escuela'),

    # (Muestra la lista de Uniformes (Camisas, Pantalones, etc.))
    path('<int:escuela_id>/uniformes/', views.listar_uniformes, name='lista_uniformes'),

    # CRUD para Uniforme Principal
    path('agregar/', views.agregar_uniforme, name='agregar_uniforme'),
    path('editar/<int:uniforme_id>/', views.editar_uniforme, name='editar_uniforme'),
    path('borrar/<int:uniforme_id>/', views.borrar_uniforme, name='borrar_uniforme'),

    # 💥 CRUD para VARIANTE (Detalle) 💥
    # Muestra todas las variantes (tallas, precios) de un Uniforme específico.
    path('<int:uniforme_id>/variantes/', views.gestionar_variantes, name='gestionar_variantes'),
    # Permite añadir una nueva variante a ese Uniforme.
    path('<int:uniforme_id>/variantes/agregar/', views.agregar_variante, name='agregar_variante'),
    # Permite editar una variante específica.
    path('variantes/editar/<int:variante_id>/', views.editar_variante, name='editar_variante'),
    # Permite borrar una variante específica.
    path('variantes/borrar/<int:variante_id>/', views.borrar_variante, name='borrar_variante'),
]