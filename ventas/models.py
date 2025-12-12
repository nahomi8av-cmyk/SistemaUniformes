# ventas/models.py
from django.db import models
from clientes.models import Cliente
from uniformes.models import VarianteUniforme
from empleados.models import Empleado
from django.contrib.auth.models import User


class Pedido(models.Model):
    idPedido = models.AutoField(primary_key=True, db_column='idpedido')
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='idcliente')
    creado_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='creado_por')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    abono_acumulado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        db_column='abono')
    estado = models.CharField(max_length=20, default='PENDIENTE')
    notas = models.TextField(
        null=True,
        blank=True,
        db_column='notas')
    def __str__(self):
        return f"Pedido #{self.pk} - Cliente: {self.idCliente.nombre}"
    class Meta:
        db_table = 'pedidos'


class DetallePedido(models.Model):
    idDetallePedido = models.AutoField(
        primary_key=True,
        db_column='iddetallep')
    idPedido = models.ForeignKey(
        'Pedido',
        on_delete=models.CASCADE,
        db_column='idpedido')
    idVariante = models.ForeignKey(
        'uniformes.VarianteUniforme',
        on_delete=models.PROTECT,
        db_column='idvariante',
        related_name = 'detalles_ventas')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = 'detalle_pedidos'
        managed = False