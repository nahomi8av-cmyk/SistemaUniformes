# clientes/admin.py

from django.contrib import admin
from .models import Cliente

class ClienteAdmin(admin.ModelAdmin):
    # Muestra ID, nombre y teléfono
    list_display = ('idCliente', 'nombre', 'telefono')
    search_fields = ('nombre', 'telefono')

admin.site.register(Cliente, ClienteAdmin)
