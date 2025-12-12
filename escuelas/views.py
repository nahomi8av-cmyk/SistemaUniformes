# escuelas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
# Asumiendo que tu modelo se llama 'Escuela'
from .models import Escuela


# --------------------
# 1. LISTAR/INDEX
# --------------------

@login_required
def listar_escuelas(request):
    escuelas = Escuela.objects.all().order_by('nombre')

    acciones = [
        {'nombre': 'Agregar Nueva Escuela', 'url': 'agregar_escuela', 'color': 'success', 'icon': 'plus'},
        {'nombre': 'Listado Completo', 'url': 'lista_escuelas', 'color': 'info', 'icon': 'list'},
    ]

    return render(request, 'escuelas/lista_escuelas.html', {
        'escuelas': escuelas,
        'acciones': acciones
    })


# --------------------
# 2. CREAR (Agregar)
# --------------------

@login_required
def agregar_escuela(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')

        if nombre:
            Escuela.objects.create(
                nombre=nombre,

            )
            return redirect('lista_escuelas')

    return render(request, 'escuelas/agregar_escuela.html')


# --------------------
# 3. MODIFICAR (Editar)
# --------------------

@login_required
def editar_escuela(request, escuela_id):

    escuela = get_object_or_404(Escuela, idEscuela=escuela_id)

    if request.method == 'POST':
        escuela.nombre = request.POST.get('nombre')

        escuela.save()

        return redirect('lista_escuelas')

    return render(request, 'escuelas/editar_escuela.html', {'escuela': escuela})


# --------------------
# 4. BORRAR (Eliminar)
# --------------------

@login_required
def borrar_escuela(request, escuela_id):
    escuela = get_object_or_404(Escuela, idEscuela=escuela_id)

    if request.method == 'POST':

        escuela.delete()
        return redirect('lista_escuelas')

    return render(request, 'escuelas/confirmar_borrar.html', {'escuela': escuela})