# ventas/admin.py

from django.contrib import admin
from .models import Pedido, DetallePedido

# 1. Define el Inline: Permite editar los DetallePedido DENTRO de la página de Pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    # Muestra los campos que se editarán
    fields = ('idVariante', 'cantidad', 'precio_unitario', 'subtotal')
    # Controla la cantidad de formularios vacíos para agregar
    extra = 1
    # Hace que los campos de cálculo (precio, subtotal) sean de solo lectura
    readonly_fields = ('precio_unitario', 'subtotal')

# 2. Define la clase Admin para Pedido
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('idPedido', 'idCliente', 'fecha', 'total', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('idCliente__nombre',) # Permite buscar por el nombre del cliente
    # Agrega el DetallePedidoInline
    inlines = [DetallePedidoInline]

# 3. Registra los modelos
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DetallePedido) # DetallePedido se registra, pero se edita principalmente vía Inline
