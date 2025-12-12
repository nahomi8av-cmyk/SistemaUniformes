# caja/models.py
from django.db import models
from django.utils import timezone
from empleados.models import Empleado  # <-- Importación necesaria

# Opciones para el campo 'tipo' en CajaMovimiento
TIPO_MOVIMIENTO_CHOICES = [
    ('ENTRADA', 'Entrada de Dinero'),
    ('SALIDA', 'Salida de Dinero'),
]


class Caja(models.Model):
    idCaja = models.AutoField(primary_key=True, db_column='idcaja')

    abierto_en = models.DateTimeField(db_column='abierto_en')
    cerrado_en = models.DateTimeField(null=True, blank=True, db_column='cerrado_en')

    fondo_inicial = models.DecimalField(max_digits=10, decimal_places=2, db_column='fondo_inicial')
    conteo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='conteo_final')
    dinero_esperado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          db_column='dinero_esperado')
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='diferencia')

    abierto_por = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='abierto_por',
        related_name='cajas_abiertas'
    )
    cerrado_por = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='cerrado_por',
        related_name='cajas_cerradas'
    )

    def __str__(self):
        return f"Caja ID {self.idCaja} - Abierta por {self.abierto_por.nombre}"

    class Meta:
        db_table = 'caja_sesiones'
        managed = False


# =========================================================================
# NUEVO MODELO: MOVIMIENTOS DE CAJA
# =========================================================================
class CajaMovimiento(models.Model):
    idMovimiento = models.AutoField(primary_key=True, db_column='idmovimiento')

    idcaja = models.ForeignKey(Caja, on_delete=models.PROTECT, db_column='idcaja')

    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES, db_column='tipo')
    monto = models.DecimalField(max_digits=10, decimal_places=2, db_column='monto')
    descripcion = models.CharField(max_length=255, db_column='descripcion')
    fecha = models.DateTimeField(default=timezone.now, db_column='fecha')

    creado_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        db_column='creado_por',
        related_name='movimientos_creados'
    )

    def __str__(self):
        return f"{self.tipo} ${self.monto} en Caja #{self.idcaja.idCaja}"

    class Meta:
        db_table = 'caja_movimientos'
        managed = False
        ordering = ['-fecha']