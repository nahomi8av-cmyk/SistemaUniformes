# empleados/models.py
from django.db import models


class Empleado(models.Model):
    # Asegúrate que el tipo de campo y el db_column coincidan con tu base de datos
    idEmpleado = models.AutoField(primary_key=True, db_column='idempleado')
    nombre = models.CharField(max_length=100)

    # 💥 CAMPOS FALTANTES AGREGADOS 💥
    usuario = models.CharField(max_length=50, unique=True, db_column='usuario')
    clave = models.CharField(max_length=128, db_column='clave')

    # Agrega otros campos esenciales que necesites (ej: apellido, puesto, etc.)

    def __str__(self):
        return f"{self.nombre} ({self.usuario} - ID: {self.idEmpleado})"


    class Meta:
            # ¡CRUCIAL! Mapea a tu tabla existente en PostgreSQL
            db_table = 'empleados'
            # Esto indica a Django que no debe migrar esta tabla si ya existe.
            # En este caso, como no vas a migrar la app 'empleados', no es estrictamente necesario,
            # pero es bueno recordarlo.
            managed = False


from django.db import models

# Create your models here.
