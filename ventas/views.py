# ventas/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from pagos.models import Pago
# Modelos necesarios
from clientes.models import Cliente

from .models import Pedido, DetallePedido  # Asumo que estos son tus modelos de ventas
from empleados.models import Empleado
from caja.models import Caja
from django.core.serializers import serialize
import json
from uniformes.models import VarianteUniforme # Necesitas importar este modelo
from decimal import Decimal

@login_required
@transaction.atomic
def nueva_venta(request):
    caja_actual = Caja.objects.filter(cerrado_en__isnull=True).first()
    if not caja_actual:
        return redirect('abrir_caja')
    if request.method == 'POST':
        # 1. Obtener datos del formulario
        cliente_id = request.POST.get('cliente_id')
        empleado_id = request.POST.get('empleado_id')
        notas_pedido = request.POST.get('notas_pedido', '').strip()
        total_pedido = 0
        try:
            cliente = Cliente.objects.get(idCliente=cliente_id)
            empleado = Empleado.objects.get(idEmpleado=empleado_id)
        except (Cliente.DoesNotExist, Empleado.DoesNotExist):
            return redirect('menu_principal')
        # 2. Crear el encabezado del pedido
        nuevo_pedido = Pedido.objects.create(
            idCliente=cliente,
            estado='PENDIENTE',
            total=0,
            creado_por=empleado,
            notas=notas_pedido,)
        # 3. Procesar los Detalles del Pedido (Items)
        variante_ids = request.POST.getlist('variante_id[]')
        cantidades = request.POST.getlist('cantidad[]')
        precios_unitarios = request.POST.getlist('precio_unitario[]')
        if not variante_ids:
            raise Exception("Debe añadir al menos un producto al pedido.")
        for vid, cant, precio in zip(variante_ids, cantidades, precios_unitarios):
            if int(cant) <= 0: continue
            variante = VarianteUniforme.objects.get(idVariante=vid)
            cantidad = int(cant)
            precio_unitario = float(precio)
            subtotal = cantidad * precio_unitario
            total_pedido += subtotal
            # Crear el detalle del pedido
            DetallePedido.objects.create(
                idPedido=nuevo_pedido,
                idVariante=variante,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal)
            variante.stock -= cantidad
            variante.save()
        # 4. Actualizar el total del encabezado del pedido
        nuevo_pedido.total = total_pedido
        nuevo_pedido.save()
        monto_abonado = request.POST.get('monto_abonado', '0')
        monto_abonado = float(monto_abonado)
        forma_pago_seleccionada = request.POST.get('forma_pago')
        # 4. Procesar el Pago Inicial
        if monto_abonado > 0:
            Pago.objects.create(
                idPedido=nuevo_pedido,
                monto=monto_abonado,
                forma_pago=forma_pago_seleccionada,
                recibido_por=empleado,
                idcaja=caja_actual,)
            nuevo_pedido.abono_acumulado = monto_abonado
            # 5. Actualizar el estado del Pedido

            if monto_abonado >= nuevo_pedido.total:
                nuevo_pedido.estado = 'PAGADO'
            else:
                nuevo_pedido.estado = 'PENDIENTE'
        # 6. Finalizar la Actualización del Pedido
        nuevo_pedido.save()
        return redirect('menu_principal')

    # Lógica para manejar la solicitud GET (Mostrar el formulario)
    else:
        clientes = Cliente.objects.all().order_by('nombre')
        empleados = Empleado.objects.all().order_by('nombre')
        variantes_query = VarianteUniforme.objects.select_related('idUniforme').all().values(
            'idVariante',
            'talla',
            'precio',
            'idUniforme__nombre'
        )
        variantes_list = list(variantes_query)
        for variante in variantes_list:
            if 'precio' in variante and variante['precio'] is not None:

                variante['precio'] = float(variante['precio'])
        variantes_json = json.dumps(variantes_list)
        contexto = {
            'titulo': 'Nueva Venta / Pedido',
            'clientes': clientes,
            'empleados': empleados,
            'caja_abierta': caja_actual,
            'variantes': variantes_json,
        }
        return render(request, 'ventas/nueva_venta.html', contexto)


@login_required
def nuevo_pago(request):
    """Muestra el formulario para registrar un abono a un pedido existente."""

    contexto = {
        'titulo': 'Registro de Pago / Abono',

    }
    return render(request, 'ventas/nuevo_pago.html', contexto)


@login_required
def detalle_pedido(request, pedido_id):

    pedido = get_object_or_404(Pedido, idPedido=pedido_id)

    detalles = DetallePedido.objects.filter(idPedido=pedido).select_related('idVariante', 'idVariante__idUniforme')

    contexto = {
        'pedido': pedido,
        'detalles': detalles,
        'titulo': f'Detalle de Pedido #{pedido.idPedido}'
    }

    return render(request, 'pedidos/detalle_pedido.html', contexto)