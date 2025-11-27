from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from functools import wraps

from .models import *
from usuarios.enums import Roles
from usuarios.views import ValidarRolUsuario


def require_tipificador_access(view_func):
    """
    Decorador de autorización para los endpoints del tipificador.

    - Requiere que el usuario esté autenticado.
    - Valida que pertenezca a uno de los roles permitidos:
      Administrador, Supervisor o Agente.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return HttpResponseForbidden("No autorizado para acceder al tipificador.")

        # Function-Level Authorization explícito
        if not (
            ValidarRolUsuario(request, Roles.ADMINISTRADOR.value) or
            ValidarRolUsuario(request, Roles.SUPERVISOR.value) or
            ValidarRolUsuario(request, Roles.AGENTE.value)
        ):
            return HttpResponseForbidden("No autorizado para acceder al tipificador.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@require_GET
@login_required
@require_tipificador_access
def ciudadano(request):
    numero_identificacion = request.GET.get('numero_identificacion')
    if not numero_identificacion:
        return JsonResponse({'error': 'Número no enviado'}, status=400)

    try:
        ciu = Ciudadano.objects.get(numero_identificacion=numero_identificacion)
        return JsonResponse({
            'id': ciu.id,
            'nombre': ciu.nombre,
            'tipo_identificacion_id': ciu.tipo_identificacion_id,
            'correo': ciu.correo,
            'telefono': ciu.telefono,
            'direccion_residencia': ciu.direccion_residencia,
            'pais_id': ciu.pais_id,
            'ciudad': ciu.ciudad,
            'sexo_id': ciu.sexo_id,
            'genero_id': ciu.genero_id,
            'orientacion_id': ciu.orientacion_id,
            'tiene_discapacidad_id': ciu.tiene_discapacidad_id,
            'discapacidad_id': ciu.discapacidad_id,
            'rango_edad_id': ciu.rango_edad_id,
            'nivel_educativo_id': ciu.nivel_educativo_id,
            'grupo_etnico_id': ciu.grupo_etnico_id,
            'grupo_poblacional_id': ciu.grupo_poblacional_id,
            'estrato_id': ciu.estrato_id,
            'localidad_id': ciu.localidad_id,
            'calidad_comunicacion_id': ciu.calidad_comunicacion_id,
        })
    except Ciudadano.DoesNotExist:
        return JsonResponse({}, status=404)


@require_GET
@login_required
@require_tipificador_access
def tipos_canal(request):
    """Obtener todos los tipos de canal"""
    tipos = TipoCanal.objects.all().values('id', 'nombre')
    return JsonResponse(list(tipos), safe=False)


@require_GET
@login_required
@require_tipificador_access
def segmentos(request):
    """Obtener segmentos por tipo de canal (excluyendo inactivos)"""
    tipo_canal_id = request.GET.get('tipo_canal_id')
    if not tipo_canal_id:
        return JsonResponse({'error': 'tipo_canal_id requerido'}, status=400)

    segmentos_inactivos = [19, 20, 23, 24, 27, 28]

    segmentos = Segmento.objects.filter(
        tipo_canal_id=tipo_canal_id
    ).exclude(
        id__in=segmentos_inactivos
    ).values('id', 'nombre', 'tiene_segmento_ii')

    return JsonResponse(list(segmentos), safe=False)


@require_GET
@login_required
@require_tipificador_access
def segmentos_ii(request):
    """Obtener segmentos II por segmento"""
    segmento_id = request.GET.get('segmento_id')
    if not segmento_id:
        return JsonResponse({'error': 'segmento_id requerido'}, status=400)

    segmentos_ii = SegmentoII.objects.filter(segmento_id=segmento_id).values('id', 'nombre')
    return JsonResponse(list(segmentos_ii), safe=False)


@require_GET
@login_required
@require_tipificador_access
def segmentos_iii(request):
    """
    Obtener segmentos III por segmento II
    Funciona de manera completamente dinámica
    """
    segmento_ii_id = request.GET.get('segmento_ii_id')
    if not segmento_ii_id:
        return JsonResponse({'error': 'segmento_ii_id requerido'}, status=400)

    try:
        segmentos_iii = SegmentoIII.objects.filter(
            segmento_ii_id=segmento_ii_id
        ).select_related('segmento_ii__segmento').values(
            'id',
            'nombre',
            'segmento_ii_id',
            'segmento_ii__nombre',
            'segmento_ii__segmento__nombre'
        ).order_by('nombre')

        data = []
        for seg_iii in segmentos_iii:
            data.append({
                'id': seg_iii['id'],
                'nombre': seg_iii['nombre'],
                'segmento_ii_id': seg_iii['segmento_ii_id'],
                'segmento_ii_nombre': seg_iii['segmento_ii__nombre'],
                'segmento_nombre': seg_iii['segmento_ii__segmento__nombre']
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
@login_required
@require_tipificador_access
def tipificaciones(request):
    """Obtener solo las tipificaciones de la nueva estructura (153-165)"""
    tipificaciones = Tipificacion.objects.filter(
        id__gte=153,
        id__lte=165
    ).values('id', 'nombre').order_by('id')
    return JsonResponse(list(tipificaciones), safe=False)


@require_GET
@login_required
@require_tipificador_access
def tipificaciones_nuevas(request):
    """API específica para las tipificaciones nuevas (153-165)"""
    tipificaciones_ids = [153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165]
    tipificaciones = Tipificacion.objects.filter(
        id__in=tipificaciones_ids
    ).values('id', 'nombre').order_by('id')
    return JsonResponse(list(tipificaciones), safe=False)


@require_GET
@login_required
@require_tipificador_access
def tipificaciones_todas(request):
    """
    Obtener TODAS las tipificaciones.
    Solo se permite a Administrador/Supervisor (Function-Level Authorization).
    No maneja objetos por usuario, solo catálogo global (Object-Level no aplica).
    """
    if not (
        ValidarRolUsuario(request, Roles.ADMINISTRADOR.value) or
        ValidarRolUsuario(request, Roles.SUPERVISOR.value)
    ):
        return HttpResponseForbidden("No autorizado para ver todas las tipificaciones.")

    tipificaciones = Tipificacion.objects.all().values('id', 'nombre').order_by('id')
    return JsonResponse(list(tipificaciones), safe=False)


@require_GET
@login_required
@require_tipificador_access
def categorias(request):
    """Obtener categorías por tipificación (catálogo global)"""
    tipificacion_id = request.GET.get('tipificacion_id')
    if not tipificacion_id:
        return JsonResponse({'error': 'tipificacion_id requerido'}, status=400)

    categorias = Categoria.objects.filter(
        tipificacion_id=tipificacion_id,
        nivel=1
    ).exclude(
        id=1018
    ).values('id', 'nombre')
    return JsonResponse(list(categorias), safe=False)


@require_GET
@login_required
@require_tipificador_access
def subcategorias(request):
    """Obtener subcategorías por categoría padre (catálogo global)"""
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)

    subcategorias = Categoria.objects.filter(
        categoria_padre_id=categoria_padre_id,
        nivel=2
    ).values('id', 'nombre')
    return JsonResponse(list(subcategorias), safe=False)


@require_GET
@login_required
@require_tipificador_access
def subcategorias_ii(request):
    """
    Obtener Sub Categorías II (nivel 3) por categoría padre
    """
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)

    try:
        subcategorias_ii = Categoria.objects.filter(
            categoria_padre_id=categoria_padre_id,
            nivel=3
        ).values('id', 'nombre').order_by('nombre')

        return JsonResponse(list(subcategorias_ii), safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
@login_required
@require_tipificador_access
def subcategorias_iii(request):
    """
    Obtener Sub Categorías III (nivel 4) por categoría padre
    """
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)

    try:
        subcategorias_iii = Categoria.objects.filter(
            categoria_padre_id=categoria_padre_id,
            nivel=4
        ).values('id', 'nombre').order_by('nombre')

        return JsonResponse(list(subcategorias_iii), safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
@login_required
@require_tipificador_access
def tipificaciones_old(request):
    """Para compatibilidad con código anterior (catálogo)"""
    segmento_id = request.GET.get('segmento_id')
    if segmento_id:
        tipificaciones = Tipificacion.objects.filter(segmento_id=segmento_id).values('id', 'nombre')
        return JsonResponse(list(tipificaciones), safe=False)
    return JsonResponse({'error': 'segmento_id requerido'}, status=400)


@require_GET
@login_required
@require_tipificador_access
def categorias_old(request):
    """Para compatibilidad con código anterior (catálogo)"""
    tipificacion_id = request.GET.get('tipificacion_id')
    if tipificacion_id:
        categorias = Categoria.objects.filter(tipificacion_id=tipificacion_id).values('id', 'nombre')
        return JsonResponse(list(categorias), safe=False)
    return JsonResponse({'error': 'tipificacion_id requerido'}, status=400)


@require_GET
@login_required
@require_tipificador_access
def segmentos_iv(request):
    segmento_iii_id = request.GET.get('segmento_iii_id')
    if not segmento_iii_id:
        return JsonResponse({'error': 'segmento_iii_id requerido'}, status=400)
    data = SegmentoIV.objects.filter(segmento_iii_id=segmento_iii_id).values('id', 'nombre').order_by('nombre')
    return JsonResponse(list(data), safe=False)


@require_GET
@login_required
@require_tipificador_access
def segmentos_v(request):
    segmento_iv_id = request.GET.get('segmento_iv_id')
    if not segmento_iv_id:
        return JsonResponse({'error': 'segmento_iv_id requerido'}, status=400)
    data = SegmentoV.objects.filter(segmento_iv_id=segmento_iv_id).values('id', 'nombre').order_by('nombre')
    return JsonResponse(list(data), safe=False)


@require_GET
@login_required
@require_tipificador_access
def segmentos_vi(request):
    segmento_v_id = request.GET.get('segmento_v_id')
    if not segmento_v_id:
        return JsonResponse({'error': 'segmento_v_id requerido'}, status=400)
    data = SegmentoVI.objects.filter(segmento_v_id=segmento_v_id).values('id', 'nombre').order_by('nombre')
    return JsonResponse(list(data), safe=False)


@require_GET
@login_required
@require_tipificador_access
def subcategorias_iv(request):
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)
    data = Categoria.objects.filter(
        categoria_padre_id=categoria_padre_id,
        nivel=4
    ).values('id', 'nombre').order_by('nombre')
    return JsonResponse(list(data), safe=False)


@require_GET
@login_required
@require_tipificador_access
def subcategorias_v(request):
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)
    data = Categoria.objects.filter(
        categoria_padre_id=categoria_padre_id,
        nivel=5
    ).values('id', 'nombre').order_by('nombre')
    return JsonResponse(list(data), safe=False)


@require_GET
@login_required
@require_tipificador_access
def niveles(request):
    """
    Devuelve categorías por nivel (1..6) y, si nivel>1, opcionalmente por padre.
    GET /api/niveles/?nivel=1
    GET /api/niveles/?nivel=2&padre_id=123

    Function-Level Authorization:
      - Requiere autenticación y rol (Administrador/Supervisor/Agente).
    Object-Level Authorization:
      - No aplica porque solo expone catálogos globales sin propiedad por usuario.
    """
    try:
        nivel = int(request.GET.get('nivel', '0'))
    except ValueError:
        return JsonResponse({'error': 'nivel inválido'}, status=400)

    if nivel < 1 or nivel > 6:
        return JsonResponse({'error': 'nivel debe estar entre 1 y 6'}, status=400)

    padre_id = request.GET.get('padre_id')
    flt = {'nivel': nivel}
    if nivel > 1:
        if not padre_id:
            return JsonResponse({'error': 'padre_id requerido para nivel > 1'}, status=400)
        flt['categoria_padre_id'] = padre_id

    data = list(Categoria.objects.filter(**flt).values('id', 'nombre').order_by('nombre'))
    return JsonResponse(data, safe=False)
