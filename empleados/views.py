# empleados/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Empleado


@login_required
def listar_empleados(request):
    empleados = Empleado.objects.all().order_by('nombre')

    return render(request, 'empleados/lista_empleados.html', {
        'empleados': empleados,
        'titulo': 'Gestión de Empleados',
    })


@login_required
def agregar_empleado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        usuario = request.POST.get('usuario')
        clave = request.POST.get('clave')

        if nombre and usuario and clave:
            Empleado.objects.create(
                nombre=nombre,
                usuario=usuario,
                clave=clave
            )
            return redirect('lista_empleados')

    return render(request, 'empleados/agregar_empleado.html')


@login_required
def editar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, idEmpleado=empleado_id)

    if request.method == 'POST':
        empleado.nombre = request.POST.get('nombre')
        empleado.usuario = request.POST.get('usuario')
        nueva_clave = request.POST.get('clave')

        if nueva_clave:
            empleado.clave = nueva_clave

        empleado.save()
        return redirect('lista_empleados')

    return render(request, 'empleados/editar_empleado.html', {'empleado': empleado})


@login_required
def borrar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, idEmpleado=empleado_id)

    if request.method == 'POST':
        try:
            empleado.delete()
            return redirect('lista_empleados')
        except Exception as e:
            error_msg = f"No se puede eliminar al empleado. Asegúrate de que no tenga registros asociados (cajas, pedidos, etc.). Error: {e}"
            return render(request, 'empleados/confirmar_borrar.html', {'empleado': empleado, 'error': error_msg})

    return render(request, 'empleados/confirmar_borrar.html', {'empleado': empleado})
