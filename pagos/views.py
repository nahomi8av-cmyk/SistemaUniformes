# pagos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from ventas.models import Pedido
from empleados.models import Empleado
from caja.models import Caja
from .models import Pago  # Tu modelo Pago
from django.db.models import Sum
from decimal import Decimal


@login_required
def buscar_pedido(request):
    pedido = None
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        if pedido_id:
            try:
                pedido = Pedido.objects.get(idPedido=pedido_id)
                return redirect('registrar_pago', pedido_id=pedido.idPedido)
            except Pedido.DoesNotExist:
                return render(request, 'pagos/buscar_pedido.html', {
                    'error': f'El ID del pedido {pedido_id} no fue encontrado.',
                    'pedido': pedido
                })
    return render(request, 'pagos/buscar_pedido.html', {
        'error': None,
        'pedido': None
    })


@login_required
@transaction.atomic
def registrar_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, idPedido=pedido_id)
    empleados = Empleado.objects.all().order_by('nombre')
    total_pagado = Pago.objects.filter(idPedido=pedido).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_pendiente = pedido.total - total_pagado
    caja_actual = Caja.objects.filter(cerrado_en__isnull=True).first()
    if not caja_actual:
        return redirect('abrir_caja')

    if request.method == 'POST':
        monto_abonado_str = request.POST.get('monto_abonado', '0')
        forma_pago_seleccionada = request.POST.get('forma_pago')
        empleado_id_receptor_str = request.POST.get('empleado_receptor_id')
        try:
            monto_abonado = Decimal(monto_abonado_str)
            empleado_receptor_id = int(empleado_id_receptor_str)
            empleado_que_recibe = Empleado.objects.get(idEmpleado=empleado_receptor_id)
        except (ValueError, Empleado.DoesNotExist):
            error = "El monto abonado o el empleado receptor son inválidos."
        if 'error' not in locals() and monto_abonado > 0 and monto_abonado <= saldo_pendiente:
            Pago.objects.create(
                idPedido=pedido,
                monto=monto_abonado,
                forma_pago=forma_pago_seleccionada,
                recibido_por=empleado_que_recibe,
                idcaja=caja_actual,)
            nuevo_abono_total = total_pagado + monto_abonado
            pedido.abono_acumulado = nuevo_abono_total
            # Actualizar estado si se liquida
            if nuevo_abono_total >= pedido.total:
                pedido.estado = 'PAGADO'
            else:
                pedido.estado = 'PENDIENTE'

            pedido.save()
            return redirect('menu_principal')
        elif 'error' not in locals():
            error = "El monto abonado es inválido o excede el saldo pendiente."


    contexto = {
        'pedido': pedido,
        'saldo_pendiente': saldo_pendiente,
        'total_pagado': total_pagado,
        'caja_actual': caja_actual,
        'formas_pago': ['EFECTIVO', 'TRANSFERENCIA'],
        'empleados': empleados,
        'error': locals().get('error', None)
    }
    return render(request, 'pagos/registrar_pago.html', contexto)


FORMAS_PAGO = [
    ('EFECTIVO', 'EFECTIVO'),
    ('TRANSFERENCIA', 'TRANSFERENCIA'),

]


# --------------------
# 1. LISTAR PAGOS
# --------------------

@login_required
def listar_pagos(request):

    pagos = Pago.objects.select_related('idPedido', 'recibido_por').order_by('-fecha_pago')

    contexto = {
        'pagos': pagos,
        'titulo': 'Listado de Pagos',
    }
    return render(request, 'pagos/listar_pagos.html', contexto)


# --------------------
# 2. MODIFICAR PAGO
# --------------------

@login_required
def editar_pago(request, pago_id):
    pago = get_object_or_404(Pago, idPago=pago_id)

    monto_anterior = pago.monto

    if request.method == 'POST':
        new_monto_str = request.POST.get('monto')
        new_forma_pago = request.POST.get('forma_pago')

        try:
            new_monto = Decimal(new_monto_str)

            if new_monto < 0:
                raise ValueError("El monto no puede ser negativo.")

            with transaction.atomic():

                # 1. ACTUALIZAR PAGO
                pago.monto = new_monto
                pago.forma_pago = new_forma_pago
                pago.save()

                # 2. ACTUALIZAR PEDIDO (AJUSTE DEL ABONO)

                diferencia = new_monto - monto_anterior

                pedido = pago.idPedido
                pedido.abono_acumulado += diferencia
                pedido.save()

            return redirect('listar_pagos')

        except ValueError as e:
            error_msg = f"Error de validación: {e}"
        except Exception as e:
            error_msg = f"Error al guardar el pago: {e}"

        return render(request, 'pagos/editar_pago.html', {
            'pago': pago,
            'formas_pago': FORMAS_PAGO,
            'error': error_msg
        })

    contexto = {
        'pago': pago,
        'formas_pago': FORMAS_PAGO,
    }
    return render(request, 'pagos/editar_pago.html', contexto)


# --------------------
# 3. ELIMINAR PAGO
# --------------------

@login_required
def eliminar_pago(request, pago_id):
    pago = get_object_or_404(Pago, idPago=pago_id)

    if request.method == 'POST':
        try:

            with transaction.atomic():

                # 1. ACTUALIZAR PEDIDO (RESTAR EL MONTO DEL ABONO)
                pedido = pago.idPedido
                pedido.abono_acumulado -= pago.monto
                pedido.save()

                # 2. ELIMINAR PAGO
                pago.delete()

            return redirect('pagos:listar_pagos')

        except Exception as e:
            error_msg = f"No se pudo eliminar el pago. Error: {e}"
            return render(request, 'pagos/confirmar_eliminar_pago.html', {'pago': pago, 'error': error_msg})

    return render(request, 'pagos/confirmar_eliminar_pago.html', {'pago': pago})