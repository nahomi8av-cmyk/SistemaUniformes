from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from .models import Caja, CajaMovimiento  # Importamos el nuevo modelo
from empleados.models import Empleado
from datetime import datetime
from pagos.models import Pago
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from django.contrib import messages  # Usamos messages para notificaciones


# ----------------------------------------------------
# FUNCIONES AUXILIARES CLAVE
# ----------------------------------------------------

def _get_caja_abierta():
    return Caja.objects.filter(cerrado_en__isnull=True).first()

@login_required
@transaction.atomic
def abrir_caja(request):

    empleados = Empleado.objects.all().order_by('nombre')
    caja_abierta_existente = _get_caja_abierta()
    if caja_abierta_existente:
        messages.warning(request, "Ya existe una caja abierta. Cierra la anterior antes de abrir una nueva.")
        return redirect('menu_principal')
    if request.method == 'POST':
        fondo_inicial_str = request.POST.get('fondo_inicial', '0.00')
        empleado_id_str = request.POST.get('empleado_id')
        if not empleado_id_str:
            return render(request, 'caja/abrir_caja.html', {
                'error': 'Error: Debe seleccionar un empleado válido.',
                'empleados': empleados
            })

        try:

            fondo_inicial = Decimal(fondo_inicial_str)
            empleado_id = int(empleado_id_str)

            empleado_que_abre = Empleado.objects.get(idEmpleado=empleado_id)

        except ValueError:
            return render(request, 'caja/abrir_caja.html', {
                'error': 'Error: El fondo inicial debe ser un número válido.',
                'empleados': empleados
            })
        except Empleado.DoesNotExist:
            return render(request, 'caja/abrir_caja.html', {
                'error': 'Error: El empleado seleccionado no existe en el sistema.',
                'empleados': empleados
            })
        Caja.objects.create(
            abierto_en=datetime.now(),
            fondo_inicial=fondo_inicial,
            abierto_por=empleado_que_abre,
        )
        messages.success(request, f"Caja abierta exitosamente con fondo inicial de ${fondo_inicial:,.2f}.")
        return redirect('menu_principal')

    return render(request, 'caja/abrir_caja.html', {'empleados': empleados})


@login_required
@transaction.atomic
def cerrar_caja(request):
    caja_a_cerrar = _get_caja_abierta()

    if not caja_a_cerrar:
        messages.error(request, "No hay caja abierta para cerrar.")
        return redirect('menu_principal')

    pagos_en_efectivo = Pago.objects.filter(
        idcaja=caja_a_cerrar,

        forma_pago='EFECTIVO'
    ).aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')


    movimientos_caja = CajaMovimiento.objects.filter(idcaja=caja_a_cerrar)

    entradas = movimientos_caja.filter(tipo='ENTRADA').aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
    salidas = movimientos_caja.filter(tipo='SALIDA').aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')

    neto_movimientos = entradas - salidas  # Puede ser positivo o negativo

    dinero_esperado = caja_a_cerrar.fondo_inicial + pagos_en_efectivo + neto_movimientos

    error = None

    if request.method == 'POST':

        conteo_final_str = request.POST.get('conteo_final')
        empleado_id_cierre = request.POST.get('empleado_cierre_id')

        try:
            conteo_final = Decimal(conteo_final_str)
            empleado_que_cierra = Empleado.objects.get(idEmpleado=empleado_id_cierre)
        except (ValueError, Empleado.DoesNotExist):
            error = "El conteo final o el empleado de cierre es inválido."
            # Recargar contexto para mostrar error
            contexto = {
                'caja': caja_a_cerrar,
                'fondo_inicial': caja_a_cerrar.fondo_inicial,
                'ingresos_efectivo': pagos_en_efectivo,
                'entradas_mov': entradas,
                'salidas_mov': salidas,
                'dinero_esperado': dinero_esperado,
                'empleados': Empleado.objects.all().order_by('nombre'),
                'error': error
            }
            return render(request, 'caja/cerrar_caja.html', contexto)

        # Si no hay errores en la captura de datos
        if not error:
            # 5. Calcular la Diferencia
            diferencia = conteo_final - dinero_esperado

            # 6. Actualizar y Cerrar la Caja
            caja_a_cerrar.cerrado_en = timezone.now()
            caja_a_cerrar.conteo_final = conteo_final
            caja_a_cerrar.dinero_esperado = dinero_esperado
            caja_a_cerrar.diferencia = diferencia
            caja_a_cerrar.cerrado_por = empleado_que_cierra

            caja_a_cerrar.save()

            if diferencia > Decimal('0.01') or diferencia < Decimal('-0.01'):
                messages.warning(request,
                                 f"Caja cerrada con una diferencia de ${diferencia:,.2f}. El monto esperado era ${dinero_esperado:,.2f}.")
            else:
                messages.success(request, "Caja cerrada correctamente, sin diferencia.")

            return redirect('menu_principal')

    # Lógica GET: Renderizar el formulario con los datos esperados
    contexto = {
        'caja': caja_a_cerrar,
        'fondo_inicial': caja_a_cerrar.fondo_inicial,
        'ingresos_efectivo': pagos_en_efectivo,
        'entradas_mov': entradas,
        'salidas_mov': salidas,
        'dinero_esperado': dinero_esperado,
        'empleados': Empleado.objects.all().order_by('nombre'),
        'error': error
    }

    return render(request, 'caja/cerrar_caja.html', contexto)


@login_required
def listar_sesiones(request):

    sesiones = Caja.objects.select_related('abierto_por', 'cerrado_por').order_by(
        '-abierto_en')

    contexto = {
        'sesiones': sesiones,
        'titulo': 'Gestión de Sesiones de Caja',
    }
    return render(request, 'caja/listar_sesiones.html', contexto)


# --------------------
# 2. MODIFICAR SESIÓN DE CAJA
# --------------------

@login_required
def editar_sesion(request, sesion_id):
    sesion = get_object_or_404(Caja, idCaja=sesion_id)

    if request.method == 'POST':

        new_efectivo_apertura_str = request.POST.get('fondo_inicial')

        try:

            new_efectivo_apertura = Decimal(new_efectivo_apertura_str)

            if new_efectivo_apertura < 0:
                raise ValueError("El monto de apertura no puede ser negativo.")

            # 1. ACTUALIZAR SESIÓN
            sesion.fondo_inicial = new_efectivo_apertura

            sesion.save()

            return redirect('listar_sesiones')

        except ValueError as e:
            error_msg = f"Error de formato o validación: {e}"
        except Exception as e:
            error_msg = f"Error al guardar la sesión: {e}"

        return render(request, 'caja/editar_sesion.html', {
            'sesion': sesion,
            'error': error_msg
        })

    contexto = {
        'sesion': sesion,
    }
    return render(request, 'caja/editar_sesion.html', contexto)


# --------------------
# 3. ELIMINAR SESIÓN DE CAJA
# --------------------

@login_required
def eliminar_sesion(request, sesion_id):
    sesion = get_object_or_404(Caja, idCaja=sesion_id)

    if request.method == 'POST':
        try:

            if sesion.cerrado_en:
                raise Exception("No se puede eliminar una sesión de caja que ya ha sido cerrada.")

            sesion.delete()


            return redirect('listar_sesiones')

        except Exception as e:
            error_msg = f"No se pudo eliminar la sesión. Error: {e}"
            return render(request, 'caja/confirmar_eliminar_sesion.html',
                          {'sesion': sesion, 'error': error_msg})

    return render(request, 'caja/confirmar_eliminar_sesion.html', {'sesion': sesion})







# ----------------------------------------------------
# NUEVAS VISTAS DE MOVIMIENTOS DE CAJA
# ----------------------------------------------------

@login_required
def listar_movimientos(request):
    """Muestra los movimientos de la caja actualmente abierta, o redirige."""
    caja_abierta = _get_caja_abierta()

    if not caja_abierta:
        messages.warning(request, "Debe abrir una caja antes de acceder al historial de movimientos.")
        return redirect('abrir_caja')  # Redirigir a abrir caja si no hay ninguna

    # Filtra solo los movimientos de la caja actual
    movimientos = CajaMovimiento.objects.filter(idcaja=caja_abierta).select_related('creado_por')

    context = {
        'caja': caja_abierta,
        'movimientos': movimientos,
    }
    return render(request, 'caja/listar_movimientos.html', context)


@login_required
@transaction.atomic
def agregar_movimiento(request):
    """Permite agregar una nueva entrada o salida de dinero."""
    caja_abierta = _get_caja_abierta()

    if not caja_abierta:
        messages.error(request, "No puede registrar un movimiento. Debe abrir una caja primero.")
        return redirect('abrir_caja')

    empleados = Empleado.objects.all().order_by('nombre')
    error = None

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        creado_por_id = request.POST.get('creado_por')

        try:
            monto_str = request.POST.get('monto')
            monto = Decimal(monto_str)

            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")

            creado_por_empleado = get_object_or_404(Empleado, idEmpleado=creado_por_id)

            CajaMovimiento.objects.create(
                idcaja=caja_abierta,
                tipo=tipo,
                monto=monto,
                descripcion=descripcion,
                creado_por=creado_por_empleado,
                fecha=timezone.now()
            )
            messages.success(request, f"Movimiento de {tipo} por ${monto:,.2f} registrado exitosamente.")
            return redirect('listar_movimientos')

        except ValueError as e:
            error = f"Error en el monto: El monto debe ser un número válido y positivo."
        except Empleado.DoesNotExist:
            error = "El empleado seleccionado no es válido."
        except Exception as e:
            error = f"Ocurrió un error al guardar: {e}"

    context = {
        'caja': caja_abierta,
        'empleados': empleados,
        'error': error,
    }
    return render(request, 'caja/agregar_movimiento.html', context)


@login_required
@transaction.atomic
def editar_movimiento(request, movimiento_id):
    """Permite editar un movimiento de caja, solo si la caja está abierta."""
    movimiento = get_object_or_404(CajaMovimiento, idMovimiento=movimiento_id)
    caja_abierta = _get_caja_abierta()
    empleados = Empleado.objects.all().order_by('nombre')
    error = None

    # 1. Seguridad: Verificar que sea la caja abierta o que no haya caja abierta
    if not caja_abierta or movimiento.idcaja != caja_abierta:
        messages.error(request, "Este movimiento pertenece a una caja ya cerrada o no es la caja activa.")
        return redirect('listar_movimientos')

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        creado_por_id = request.POST.get('creado_por')

        try:
            monto_str = request.POST.get('monto')
            monto = Decimal(monto_str)

            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")

            movimiento.tipo = tipo
            movimiento.monto = monto
            movimiento.descripcion = descripcion
            movimiento.creado_por = get_object_or_404(Empleado, idEmpleado=creado_por_id)
            movimiento.save()

            messages.success(request, f"Movimiento #{movimiento.idMovimiento} actualizado exitosamente.")
            return redirect('listar_movimientos')

        except ValueError:
            error = "Error en el monto: El monto debe ser un número válido y positivo."
        except Empleado.DoesNotExist:
            error = "El empleado seleccionado no es válido."
        except Exception as e:
            error = f"Ocurrió un error al guardar: {e}"

    context = {
        'movimiento': movimiento,
        'empleados': empleados,
        'error': error,
        'caja_abierta': caja_abierta,
    }
    return render(request, 'caja/editar_movimiento.html', context)


@login_required
def borrar_movimiento(request, movimiento_id):
    """Permite borrar un movimiento de caja, solo si la caja está abierta."""
    movimiento = get_object_or_404(CajaMovimiento, idMovimiento=movimiento_id)
    caja_abierta = _get_caja_abierta()

    # 1. Seguridad: Verificar que sea la caja abierta
    if not caja_abierta or movimiento.idcaja != caja_abierta:
        messages.error(request,
                       "No se puede borrar este movimiento. Pertenece a una caja ya cerrada o no es la caja activa.")
        return redirect('listar_movimientos')

    if request.method == 'POST':
        try:
            movimiento.delete()
            messages.success(request, "Movimiento eliminado correctamente.")
            return redirect('listar_movimientos')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al eliminar el movimiento: {e}")
            return redirect('listar_movimientos')

    return render(request, 'caja/confirmar_borrar_movimiento.html', {'movimiento': movimiento})