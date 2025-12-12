# escuelas/models.py

from django.db import models


class Escuela(models.Model):

    idEscuela = models.AutoField(primary_key=True, db_column='idescuela')

    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'escuelas'