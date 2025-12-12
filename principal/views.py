# principal/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from caja.models import Caja  # ¡Importa el modelo Caja!


@login_required
def menu_principal(request):
    caja_abierta = Caja.objects.filter(cerrado_en__isnull=True).first()

    contexto = {
        'caja_abierta': caja_abierta,  # Se envía al HTML
        'username': request.user.username,
        'app_version': '1.0',
    }

    return render(request, 'menu_principal.html', contexto)
