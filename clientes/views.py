# clientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q  # Para búsquedas OR
from ventas.models import Pedido
from .models import Cliente  # Asegúrate de importar tu modelo Cliente
from decimal import Decimal

@login_required
def buscar_cliente(request):
    resultados = None
    query = request.GET.get('q')
    if query:
        try:
            query_id = int(query)
            q_objects = Q(idCliente=query_id)
        except ValueError:
            q_objects = Q(nombre__icontains=query)
        resultados = Cliente.objects.filter(q_objects).order_by('nombre')
    return render(request, 'clientes/buscar_cliente.html', {
        'query': query,
        'resultados': resultados
    })

from django.db.models import Sum


@login_required
def perfil_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, idCliente=cliente_id)
    pedidos_historial = Pedido.objects.filter(idCliente=cliente).order_by('-fecha')
    total_gastado = pedidos_historial.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    contexto = {
        'cliente': cliente,
        'historial': pedidos_historial,
        'total_gastado': total_gastado,
        'num_pedidos': pedidos_historial.count()
    }
    return render(request, 'clientes/perfil_cliente.html', contexto)


# --------------------
# 1. LISTAR / INDEX CRUD (Punto de entrada)
# --------------------

@login_required
def listar_clientes(request):
    clientes = Cliente.objects.all().order_by('nombre')

    contexto = {
        'clientes': clientes,
        'titulo': 'Gestión de Clientes',
    }

    return render(request, 'clientes/lista_clientes.html', contexto)


# --------------------
# 2. CREAR (Agregar)
# --------------------

@login_required
def agregar_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')

        if nombre:
            Cliente.objects.create(
                nombre=nombre,
                telefono=telefono
            )
            return redirect('lista_clientes')

    return render(request, 'clientes/agregar_cliente.html')


# --------------------
# 3. MODIFICAR (Editar)
# --------------------

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, idCliente=cliente_id)

    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre')
        cliente.telefono = request.POST.get('telefono')
        cliente.save()

        return redirect('lista_clientes')

    return render(request, 'clientes/editar_cliente.html', {'cliente': cliente})


# --------------------
# 4. BORRAR (Eliminar)
# --------------------

@login_required
def borrar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, idCliente=cliente_id)

    if request.method == 'POST':
        try:
            cliente.delete()
            return redirect('lista_clientes')
        except Exception as e:
            error_msg = f"No se puede eliminar al cliente porque tiene pedidos asociados. Error: {e}"
            return render(request, 'clientes/confirmar_borrar.html', {'cliente': cliente, 'error': error_msg})

    return render(request, 'clientes/confirmar_borrar.html', {'cliente': cliente})