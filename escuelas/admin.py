# escuelas/admin.py

from django.contrib import admin
from .models import Escuela

# Opcional: Define una clase Admin para mejorar la vista
class EscuelaAdmin(admin.ModelAdmin):
    # Muestra el ID y el nombre en la lista
    list_display = ('idEscuela', 'nombre')
    # Permite buscar por nombre
    search_fields = ('nombre',)

admin.site.register(Escuela, EscuelaAdmin)
