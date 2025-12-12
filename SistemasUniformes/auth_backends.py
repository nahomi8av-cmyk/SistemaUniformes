import psycopg2
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
# Importamos Group para manejar los grupos/roles de Django
from django.contrib.auth.models import User, Group
from django.db import transaction


class PostgresRoleBackend(BaseBackend):
    # ... (La función get_user se mantiene igual)

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # 1. Configuración de la base de datos
        db_settings = settings.DATABASES.get('default', {})
        host = db_settings.get('HOST', 'localhost')
        port = db_settings.get('PORT', '5432')
        name = db_settings.get('NAME')

        roles_pg = []
        conn = None

        try:
            # 2. INTENTO DE AUTENTICACIÓN (Conexión exitosa = Credenciales válidas)
            conn = psycopg2.connect(
                dbname=name,
                user=username,
                password=password,
                host=host,
                port=port,
                connect_timeout=5
            )
            cursor = conn.cursor()

            # 3. AUTORIZACIÓN: OBTENER LOS ROLES/GRUPOS DE PG A LOS QUE PERTENECE ESTE USUARIO
            # Esta consulta obtiene los roles/grupos de PostgreSQL a los que pertenece el usuario
            # Necesitas tener un rol principal (ej. SUPERVISOR) que hereda de otros roles.
            cursor.execute("""
                SELECT rolname 
                FROM pg_roles 
                WHERE oid IN (
                    SELECT roleid FROM pg_auth_members 
                    WHERE member = (SELECT usesysid FROM pg_user WHERE usename = %s)
                ) OR rolname = %s;
            """, (username, username))

            # Añadimos el propio username como rol (ej. 'SUPERVISOR')
            roles_pg = [row[0] for row in cursor.fetchall()]

            conn.close()

            # 4. MANEJO DEL USUARIO EN DJANGO
            with transaction.atomic():
                user_django, created = User.objects.get_or_create(username=username)

                if created:
                    user_django.is_active = True
                    user_django.set_unusable_password()

                user_django.save()

                # 5. SINCRONIZACIÓN DE GRUPOS DE DJANGO

                # Limpiamos los grupos anteriores para evitar conflictos
                user_django.groups.clear()

                for role_name in roles_pg:
                    # Busca el grupo de Django con el nombre del rol de PG
                    group, _ = Group.objects.get_or_create(name=role_name.upper())
                    user_django.groups.add(group)

                return user_django

        except psycopg2.OperationalError as e:
            # Fallo de credenciales
            return None
        except Exception as e:
            # Otros errores (ej. DB no accesible)
            print(f"Error durante la autenticación/sincronización: {e}")
            return None

    def get_user(self, user_id):
        # ... (Función get_user se mantiene igual)
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None