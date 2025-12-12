from django.db import models
from ventas.models import Pedido
from django.contrib.auth.models import User
from empleados.models import Empleado
from caja.models import Caja

class Pago(models.Model):
    idPago = models.AutoField(primary_key=True, db_column='idpago')
    idPedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='idpedido')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pago = models.CharField(max_length=50, db_column='forma_pago')
    # Usamos Empleado para saber quién recibió el dinero
    recibido_por = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, db_column='recibido_por')
    idcaja = models.ForeignKey(
        Caja,
        on_delete=models.PROTECT,
        db_column='idcaja'  # Mantenemos el nombre de la columna existente en la DB
    )
    fecha_pago = models.DateTimeField(auto_now_add=True, db_column='fecha')

    class Meta:
        db_table = 'pagos'
        managed = False
