from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Uniforme, VarianteUniforme
from escuelas.models import Escuela  # Importa el modelo Escuela
from django.db import IntegrityError


# ----------------------------------------------------
# 0. NUEVA VISTA DE SELECCIÓN DE ESCUELA (Punto de entrada)
# ----------------------------------------------------

@login_required
def seleccionar_escuela(request):
    """Muestra la lista de escuelas para que el usuario elija de cuál ver los uniformes."""
    # Recupera todas las escuelas y pre-calcula el número de uniformes para cada una
    escuelas = Escuela.objects.all().order_by('nombre')

    # Nota: uniforme_set.count() funciona automáticamente porque definimos la FK en Uniforme
    return render(request, 'uniformes/seleccionar_escuela.html',
                  {'escuelas': escuelas, 'titulo': 'Seleccionar Escuela'})


# ----------------------------------------------------
# 1. CRUD UNIFORME (Maestro)
# ----------------------------------------------------

@login_required
def listar_uniformes(request, escuela_id):
    escuela = get_object_or_404(Escuela, idEscuela=escuela_id)
    uniformes = Uniforme.objects.filter(idEscuela=escuela).order_by('nombre')

    request.session['uniformes_escuela_id'] = escuela_id

    return render(request, 'uniformes/lista_uniformes.html', {
        'uniformes': uniformes,
        'escuela': escuela,
    })


@login_required
def agregar_uniforme(request):

    escuelas = Escuela.objects.all().order_by('nombre')
    escuela_seleccionada_id = request.session.get('uniformes_escuela_id')
    error_msg = None

    if request.method == 'POST':
        # 2. Recuperar los datos del POST
        idescuela_id = request.POST.get('idescuela')
        nombre = request.POST.get('nombre')

        if not idescuela_id or not nombre:
            error_msg = "Debe seleccionar una Escuela y especificar el Nombre del Uniforme."
            return render(request, 'uniformes/agregar_uniforme.html', {'escuelas': escuelas, 'error_msg': error_msg})

        try:
            # 3. Obtener el objeto Escuela y crear el Uniforme
            escuela_obj = get_object_or_404(Escuela, idEscuela=idescuela_id)

            Uniforme.objects.create(
                idEscuela=escuela_obj,
                nombre=nombre,

            )

            # Redirigir al listado filtrado de la escuela que acaba de usarse
            return redirect('lista_uniformes', escuela_id=idescuela_id)

        except Exception as e:
            error_msg = f"Ocurrió un error al guardar el uniforme: {e}"

    # Renderiza la plantilla, pasando las escuelas y la escuela seleccionada por defecto
    return render(request, 'uniformes/agregar_uniforme.html', {
        'escuelas': escuelas,
        'error_msg': error_msg,
        'escuela_seleccionada_id': escuela_seleccionada_id,
    })


@login_required
def editar_uniforme(request, uniforme_id):

    uniforme = get_object_or_404(Uniforme, idUniforme=uniforme_id)
    escuelas = Escuela.objects.all().order_by('nombre')

    escuela_id_actual = uniforme.idEscuela.idEscuela

    if request.method == 'POST':
        uniforme.nombre = request.POST.get('nombre')
        idescuela_id = request.POST.get('idescuela')

        if idescuela_id:
            uniforme.idEscuela = get_object_or_404(Escuela, idEscuela=idescuela_id)

        uniforme.save()

        return redirect('lista_uniformes', escuela_id=uniforme.idEscuela.idEscuela)

    return render(request, 'uniformes/editar_uniforme.html', {'uniforme': uniforme, 'escuelas': escuelas})


@login_required
def borrar_uniforme(request, uniforme_id):

    uniforme = get_object_or_404(Uniforme, idUniforme=uniforme_id)
    escuela_id = uniforme.idEscuela.idEscuela

    if request.method == 'POST':
        try:
            uniforme.delete()
            return redirect('lista_uniformes', escuela_id=escuela_id)
        except IntegrityError:
            error_msg = "No se puede eliminar este uniforme porque tiene variantes (tallas) o pedidos asociados."
            return render(request, 'uniformes/confirmar_borrar_uniforme.html',
                          {'uniforme': uniforme, 'error': error_msg})

    return render(request, 'uniformes/confirmar_borrar_uniforme.html', {'uniforme': uniforme})


# ----------------------------------------------------
# 2. CRUD VARIANTE (Detalle) - No requiere cambios en la lógica de redirección
# ----------------------------------------------------

@login_required
def gestionar_variantes(request, uniforme_id):

    uniforme = get_object_or_404(Uniforme, idUniforme=uniforme_id)

    variantes = VarianteUniforme.objects.filter(idUniforme=uniforme).order_by('talla')

    return render(request, 'uniformes/gestionar_variantes.html', {
        'uniforme': uniforme,
        'variantes': variantes,
    })


@login_required
def agregar_variante(request, uniforme_id):

    uniforme = get_object_or_404(Uniforme, idUniforme=uniforme_id)

    if request.method == 'POST':
        talla = request.POST.get('talla')
        try:
            precio = float(request.POST.get('precio'))
            stock = int(request.POST.get('stock'))
        except (ValueError, TypeError):
            error_msg = "El precio y el stock deben ser valores numéricos válidos."
            return render(request, 'uniformes/agregar_variante.html', {'uniforme': uniforme, 'error': error_msg})

        if talla and precio is not None and stock is not None:
            VarianteUniforme.objects.create(
                idUniforme=uniforme,
                talla=talla,
                precio=precio,
                stock=stock
            )
            return redirect('gestionar_variantes', uniforme_id=uniforme.idUniforme)

    return render(request, 'uniformes/agregar_variante.html', {'uniforme': uniforme})


@login_required
def editar_variante(request, variante_id):

    variante = get_object_or_404(VarianteUniforme, idVariante=variante_id)

    if request.method == 'POST':
        try:
            variante.talla = request.POST.get('talla')
            variante.precio = float(request.POST.get('precio'))
            variante.stock = int(request.POST.get('stock'))
        except (ValueError, TypeError):
            error_msg = "El precio y el stock deben ser valores numéricos válidos."
            return render(request, 'uniformes/editar_variante.html', {'variante': variante, 'error': error_msg})

        variante.save()
        return redirect('gestionar_variantes', uniforme_id=variante.idUniforme.idUniforme)

    return render(request, 'uniformes/editar_variante.html', {'variante': variante})


@login_required
def borrar_variante(request, variante_id):

    variante = get_object_or_404(VarianteUniforme, idVariante=variante_id)
    uniforme_id = variante.idUniforme.idUniforme

    if request.method == 'POST':
        variante.delete()
        return redirect('gestionar_variantes', uniforme_id=uniforme_id)

    return render(request, 'uniformes/confirmar_borrar_variante.html', {'variante': variante})