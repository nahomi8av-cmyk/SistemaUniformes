# principal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Asigna la vista a la URL raíz de esta aplicación
    path('', views.menu_principal, name='menu_principal'),
]