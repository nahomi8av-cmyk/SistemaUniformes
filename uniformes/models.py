# uniformes/models.py
from django.db import models
from escuelas.models import Escuela

class Uniforme(models.Model):
    idUniforme = models.AutoField(primary_key=True, db_column='iduniforme')
    idEscuela = models.ForeignKey(
        Escuela,
        on_delete=models.PROTECT,
        db_column='idescuela', )
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'uniformes'
        managed = False

class VarianteUniforme(models.Model):
    idVariante = models.AutoField(primary_key=True, db_column='idvariante')
    idUniforme = models.ForeignKey(
        Uniforme,
        on_delete=models.CASCADE,
        db_column='iduniforme',
        to_field='idUniforme')
    talla = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.idUniforme.nombre} - Talla: {self.talla}"
    class Meta:
        unique_together = (('idUniforme', 'talla'),)
        db_table = 'variantes_u'
        managed = False