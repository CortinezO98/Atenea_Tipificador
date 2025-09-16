from django.http import JsonResponse
from .models import *

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
        })
    except Ciudadano.DoesNotExist:
        return JsonResponse({}, status=404)

def tipos_canal(request):
    """Obtener todos los tipos de canal"""
    tipos = TipoCanal.objects.all().values('id', 'nombre')
    return JsonResponse(list(tipos), safe=False)

def segmentos(request):
    """Obtener segmentos por tipo de canal (excluyendo inactivos)"""
    tipo_canal_id = request.GET.get('tipo_canal_id')
    if not tipo_canal_id:
        return JsonResponse({'error': 'tipo_canal_id requerido'}, status=400)
    
    # IDs de los segmentos que NO quieres mostrar (según tu diccionario original)
    segmentos_inactivos = [19, 20, 23, 24, 27, 28]  # NIVEL I y NIVEL II
    
    segmentos = Segmento.objects.filter(
        tipo_canal_id=tipo_canal_id
    ).exclude(
        id__in=segmentos_inactivos
    ).values('id', 'nombre', 'tiene_segmento_ii')
    
    return JsonResponse(list(segmentos), safe=False)

def segmentos_ii(request):
    """Obtener segmentos II por segmento"""
    segmento_id = request.GET.get('segmento_id')
    if not segmento_id:
        return JsonResponse({'error': 'segmento_id requerido'}, status=400)
    
    segmentos_ii = SegmentoII.objects.filter(segmento_id=segmento_id).values('id', 'nombre')
    return JsonResponse(list(segmentos_ii), safe=False)

def segmentos_iii(request):
    """
    Obtener segmentos III por segmento II
    Funciona de manera completamente dinámica
    """
    segmento_ii_id = request.GET.get('segmento_ii_id')
    if not segmento_ii_id:
        return JsonResponse({'error': 'segmento_ii_id requerido'}, status=400)
    
    try:
        # Buscar SegmentosIII para este segmento_ii
        segmentos_iii = SegmentoIII.objects.filter(
            segmento_ii_id=segmento_ii_id
        ).select_related('segmento_ii__segmento').values(
            'id', 
            'nombre',
            'segmento_ii_id',
            'segmento_ii__nombre',
            'segmento_ii__segmento__nombre'
        ).order_by('nombre')
        
        # Formatear la respuesta
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

# ==================== TIPIFICACIONES ACTUALIZADAS ====================

def tipificaciones(request):
    """Obtener solo las tipificaciones de la nueva estructura (153-162)"""
    tipificaciones = Tipificacion.objects.filter(
        id__gte=153,  # Mayor o igual a 153
        id__lte=165   # Menor o igual a 165
    ).values('id', 'nombre').order_by('id')
    return JsonResponse(list(tipificaciones), safe=False)

def tipificaciones_nuevas(request):
    """API específica para las tipificaciones nuevas (153-162)"""
    tipificaciones_ids = [153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165]
    tipificaciones = Tipificacion.objects.filter(
        id__in=tipificaciones_ids
    ).values('id', 'nombre').order_by('id')
    return JsonResponse(list(tipificaciones), safe=False)

def tipificaciones_todas(request):
    """Obtener TODAS las tipificaciones (para uso administrativo si es necesario)"""
    tipificaciones = Tipificacion.objects.all().values('id', 'nombre').order_by('id')
    return JsonResponse(list(tipificaciones), safe=False)

# ==================== RESTO DE APIs ====================

def categorias(request):
    """Obtener categorías por tipificación"""
    tipificacion_id = request.GET.get('tipificacion_id')
    if not tipificacion_id:
        return JsonResponse({'error': 'tipificacion_id requerido'}, status=400)
    
    categorias = Categoria.objects.filter(
        tipificacion_id=tipificacion_id,
        nivel=1  # Solo categorías de nivel 1
    ).exclude(
        id=1018
    ).values('id', 'nombre')
    return JsonResponse(list(categorias), safe=False)

def subcategorias(request):
    """Obtener subcategorías por categoría padre"""
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)
    
    subcategorias = Categoria.objects.filter(
        categoria_padre_id=categoria_padre_id,
        nivel=2  # Solo subcategorías de nivel 2
    ).values('id', 'nombre')
    return JsonResponse(list(subcategorias), safe=False)

# ==================== NUEVAS APIS PARA SUB CATEGORÍAS II Y III ====================

def subcategorias_ii(request):
    """
    Obtener Sub Categorías II (nivel 3) por categoría padre
    Específicamente para PSICOLOGIA
    """
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)
    
    try:
        subcategorias_ii = Categoria.objects.filter(
            categoria_padre_id=categoria_padre_id,
            nivel=3  # Sub Categorías II son nivel 3
        ).values('id', 'nombre').order_by('nombre')
        
        return JsonResponse(list(subcategorias_ii), safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def subcategorias_iii(request):
    """
    Obtener Sub Categorías III (nivel 4) por categoría padre
    Específicamente para ADULTO cuando viene de PSICOLOGIA
    """
    categoria_padre_id = request.GET.get('categoria_padre_id')
    if not categoria_padre_id:
        return JsonResponse({'error': 'categoria_padre_id requerido'}, status=400)
    
    try:
        subcategorias_iii = Categoria.objects.filter(
            categoria_padre_id=categoria_padre_id,
            nivel=4  # Sub Categorías III son nivel 4
        ).values('id', 'nombre').order_by('nombre')
        
        return JsonResponse(list(subcategorias_iii), safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ==================== FUNCIONES DE COMPATIBILIDAD ====================

def tipificaciones_old(request):
    """Para compatibilidad con código anterior"""
    segmento_id = request.GET.get('segmento_id')
    if segmento_id:
        tipificaciones = Tipificacion.objects.filter(segmento_id=segmento_id).values('id', 'nombre')
        return JsonResponse(list(tipificaciones), safe=False)
    return JsonResponse({'error': 'segmento_id requerido'}, status=400)

def categorias_old(request):
    """Para compatibilidad con código anterior"""
    tipificacion_id = request.GET.get('tipificacion_id')
    if tipificacion_id:
        categorias = Categoria.objects.filter(tipificacion_id=tipificacion_id).values('id', 'nombre')
        return JsonResponse(list(categorias), safe=False)
    return JsonResponse({'error': 'tipificacion_id requerido'}, status=400)