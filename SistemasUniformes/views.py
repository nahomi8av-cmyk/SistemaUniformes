# SistemasUniformes/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def menu_principal(request):
    return render(request, 'menu_principal.html')

@login_required
def abrir_caja(request):
    """Placeholder para la función de Abrir Caja."""
    return render(request, 'caja/abrir_caja.html', {'titulo': 'Abrir Caja y Turno'})