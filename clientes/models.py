# clientes/models.py
from django.db import models


class Cliente(models.Model):
    idCliente = models.AutoField(primary_key=True, db_column='idcliente')
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'clientes'
