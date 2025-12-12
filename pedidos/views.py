from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from ventas.models import Pedido, DetallePedido


# --------------------
# 1. LISTAR / INDEX
# --------------------

@login_required
def listar_pedidos(request):
    pedidos = Pedido.objects.select_related('idCliente', 'creado_por').order_by('-fecha')
    contexto = {
        'pedidos': pedidos,
        'username': request.user.username,
        'titulo': 'Gestión de Pedidos',
    }
    return render(request, 'pedidos/listar_pedidos.html', contexto)


# --------------------
# 2. MODIFICAR (Editar)
# --------------------

@login_required
def editar_pedido(request, pedido_id):
    # Obtener el pedido por su clave primaria o devolver 404
    pedido = get_object_or_404(Pedido, idPedido=pedido_id)

    # Obtener el listado de todos los posibles estados del pedido (definidos en el modelo)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
        ('ENTREGADO', 'Entregado'),
    ]
    estados = ESTADOS

    if request.method == 'POST':
        # 1. Obtener datos del formulario POST
        new_total = request.POST.get('total')
        new_abono = request.POST.get('abono')
        new_estado = request.POST.get('estado')
        new_notas = request.POST.get('notas')

        # 2. Asignar y Guardar los nuevos valores
        try:
            pedido.total = new_total
            pedido.abono = new_abono
            pedido.estado = new_estado
            pedido.notas = new_notas

            # Guardamos los cambios en la base de datos
            pedido.save()
            return redirect('pedidos:listar_pedidos')

        except Exception as e:
            # Capturar errores (ej. valor numérico inválido, estado no permitido)
            error_msg = f"Error al guardar el pedido: {e}"
            return render(request, 'pedidos/editar_pedido.html', {
                'pedido': pedido,
                'estados': estados,
                'error': error_msg
            })

    contexto = {
        'pedido': pedido,
        'estados': estados,
    }
    return render(request, 'pedidos/editar_pedido.html', contexto)


# --------------------
# 3. BORRAR (Eliminar)
# --------------------

@login_required
def eliminar_pedido(request, pedido_id):
    # Obtener el pedido por su clave primaria o devolver 404
    pedido = get_object_or_404(Pedido, idPedido=pedido_id)

    if request.method == 'POST':
        try:
            # La relación DetallePedido debe tener ON DELETE CASCADE, por lo que
            # al borrar el pedido, sus detalles se borrarán automáticamente.
            pedido.delete()
            return redirect('pedidos:listar_pedidos')
        except Exception as e:
            # Manejo de error si el borrado falla (ej. restricción de base de datos)
            error_msg = f"No se pudo eliminar el pedido. Error: {e}"
            return render(request, 'pedidos/confirmar_eliminar.html', {'pedido': pedido, 'error': error_msg})

    return render(request, 'pedidos/confirmar_eliminar.html', {'pedido': pedido})
