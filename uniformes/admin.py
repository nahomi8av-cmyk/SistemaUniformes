# uniformes/admin.py

from django.contrib import admin
from .models import Uniforme, VarianteUniforme

# Opcional: Esto mejora la visualización de la lista
class UniformeAdmin(admin.ModelAdmin):
    list_display = ('idUniforme', 'nombre', 'idEscuela')
    search_fields = ('nombre',)
    list_filter = ('idEscuela',)

admin.site.register(Uniforme, UniformeAdmin)
admin.site.register(VarianteUniforme)

# Repite esto para Escuela en escuelas/admin.py, etc.
