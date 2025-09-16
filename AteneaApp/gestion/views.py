from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_GET
from django.utils.timezone import now, make_aware, localtime
from usuarios.views import ValidarRolUsuario, en_grupo
from usuarios.enums import Roles
from .models import *
from .utils import RegistrarError, get_ciudadano_anonimo  
from io import BytesIO
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from datetime import date, datetime, timedelta
import openpyxl
from openpyxl.utils import get_column_letter
import inspect

def index(request):
    if request.user.is_authenticated:
        if ValidarRolUsuario(request, Roles.ADMINISTRADOR.value):
            return redirect('dashboard_admin')
        elif ValidarRolUsuario(request, Roles.SUPERVISOR.value):
            return redirect('dashboard_supervisor')
        elif ValidarRolUsuario(request, Roles.AGENTE.value):
            return redirect('dashboard_agente')
        elif ValidarRolUsuario(request, Roles.ABOGADO.value):  # NUEVA REDIRECCIÓN
            return redirect('dashboard_abogado')
        
        messages.warning(request, "Usted no esta autorizado.")
        return redirect('logout')
    else:
        return redirect('login')


@login_required
@en_grupo([Roles.ADMINISTRADOR.value, Roles.SUPERVISOR.value, Roles.AGENTE.value])
def crear_evaluacion(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                numero_doc = (request.POST.get('numero_identificacion') or '').strip()
                es_anonimo = (request.POST.get('es_anonimo') == '1') or (numero_doc in ('9999', '9999999'))
                if es_anonimo:
                    ciudadano = get_ciudadano_anonimo()
                else:
                    cid = request.POST.get('cuidadano_id')
                    if cid:
                        ciudadano = Ciudadano.objects.get(id=cid)
                        ciudadano.tipo_identificacion_id = request.POST['tipo_identificacion']
                        ciudadano.numero_identificacion   = request.POST['numero_identificacion']
                        ciudadano.nombre                  = request.POST['nombre']
                        ciudadano.correo                  = request.POST.get('correo', '')
                        ciudadano.telefono                = request.POST.get('telefono', '')
                        ciudadano.direccion_residencia    = request.POST.get('direccion_residencia', '')
                        ciudadano.pais_id                 = request.POST.get('pais') or None
                        ciudadano.ciudad                  = request.POST.get('ciudad', '')
                        ciudadano.save()
                    else:
                        ciudadano = Ciudadano.objects.create(
                            tipo_identificacion_id=request.POST['tipo_identificacion'],
                            numero_identificacion=request.POST['numero_identificacion'],
                            nombre=request.POST['nombre'],
                            correo=request.POST.get('correo', ''),
                            telefono=request.POST.get('telefono', ''),
                            direccion_residencia=request.POST.get('direccion_residencia', ''),
                            pais_id=request.POST.get('pais') or None,
                            ciudad=request.POST.get('ciudad', '')
                        )

                # PROCESAMIENTO DE CATEGORÍAS 
                categoria_final_id = None
                if request.POST.get('subcategoria_iii'):
                    categoria_final_id = request.POST.get('subcategoria_iii')
                elif request.POST.get('subcategoria_ii'):
                    categoria_final_id = request.POST.get('subcategoria_ii')
                elif request.POST.get('subcategoria'):
                    categoria_final_id = request.POST.get('subcategoria')
                elif request.POST.get('categoria'):
                    categoria_final_id = request.POST.get('categoria')
                if categoria_final_id == "0":
                    categoria_final_id = None


                se_comunica_uri = request.POST.get('se_comunica_uri')
                se_comunica_uri_bool = True if se_comunica_uri == '1' else False if se_comunica_uri == '0' else None
                ciudad_municipio_uri = request.POST.get('ciudad_municipio_uri', '') if se_comunica_uri_bool else ''

                consulta_juridica = request.POST.get('consulta_juridica')
                consulta_juridica_bool = True if consulta_juridica == '1' else False if consulta_juridica == '0' else None
                abogado_id = request.POST.get('abogado') or None if consulta_juridica_bool else None

                tel_inconser = request.POST.get('telefono_inconser') or request.POST.get('telefono_inconcer') or ''
                evaluacion = Evaluacion.objects.create(
                    conversacion_id=request.POST['conversacion_id'],
                    observacion=request.POST['observacion'],
                    ciudadano=ciudadano,
                    user=request.user,

                    tipo_canal_id=request.POST.get('tipo_canal'),
                    segmento_id=request.POST.get('segmento'),
                    segmento_ii_id=request.POST.get('segmento_ii') or None,
                    segmento_iii_id=request.POST.get('segmento_iii') or None,
                    tipificacion_id=request.POST.get('tipificacion'),
                    categoria_id=categoria_final_id,

                    cual_otro_delito=request.POST.get('cual_otro_delito', ''),
                    se_comunica_uri=se_comunica_uri_bool,
                    ciudad_municipio_uri=ciudad_municipio_uri,
                    consulta_juridica=consulta_juridica_bool,
                    abogado_id=abogado_id,

                    # Guardar contactos SOLO si es anónimo 
                    es_anonimo=es_anonimo,
                    contacto_correo   = (request.POST.get('correo', '')   if es_anonimo else None),
                    contacto_telefono = (request.POST.get('telefono', '') if es_anonimo else None),
                    contacto_telefono_inconcer = tel_inconser,
                )

                debug_info = {
                    'tipo_canal': request.POST.get('tipo_canal'),
                    'segmento': request.POST.get('segmento'),
                    'segmento_ii': request.POST.get('segmento_ii'),
                    'segmento_iii': request.POST.get('segmento_iii'),
                    'tipificacion': request.POST.get('tipificacion'),
                    'categoria': request.POST.get('categoria'),
                    'subcategoria': request.POST.get('subcategoria'),
                    'subcategoria_ii': request.POST.get('subcategoria_ii'),
                    'subcategoria_iii': request.POST.get('subcategoria_iii'),
                    'categoria_final_id': categoria_final_id,
                    'es_anonimo': es_anonimo,
                    'telefono_inconcer': tel_inconser,
                }
                print(f"DEBUG - Crear evaluación: {debug_info}")

                if consulta_juridica_bool and abogado_id:
                    try:
                        abogado = Abogado.objects.get(id=abogado_id)
                        prioridad = determinar_prioridad_caso(evaluacion)
                        CasoAbogado.objects.create(
                            evaluacion=evaluacion,
                            abogado=abogado,
                            prioridad=prioridad,
                            estado='PENDIENTE'
                        )
                        messages.success(
                            request,
                            f"Evaluación guardada correctamente. Caso asignado automáticamente al abogado {abogado.nombre}."
                        )
                    except Abogado.DoesNotExist:
                        messages.warning(request, "Evaluación guardada, pero el abogado seleccionado no existe.")
                else:
                    messages.success(request, "Evaluación guardada correctamente.")

        except Exception as e:
            RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
            messages.error(request, f"Ocurrió un error al guardar la evaluación: {str(e)}")

        return redirect('index')

    tiposIdentificacion = TipoIdentificacion.objects.all()
    tipos_canal = TipoCanal.objects.all()
    paises = Pais.objects.all()
    abogados = Abogado.objects.filter(activo=True).order_by('nombre')

    if not tiposIdentificacion or not tipos_canal:
        messages.warning(request, "En este momento no es posible generar una tipificación. Por favor, contacte a soporte.")
        return redirect('index')

    return render(request, 'usuarios/evaluaciones/crear_evaluacion.html', {
        'tiposIdentificacion': tiposIdentificacion,
        'tipos_canal': tipos_canal,
        'paises': paises,
        'abogados': abogados,
        'is_supervisor': (
            ValidarRolUsuario(request, Roles.SUPERVISOR.value)
            or ValidarRolUsuario(request, Roles.ADMINISTRADOR.value)
        ),
        'numero_anonimo': '9999999',
    })

# ==================== FUNCIÓN AUXILIAR ACTUALIZADA ====================

def determinar_prioridad_caso(evaluacion):
    """
    Determina la prioridad del caso basado en la tipificación o categoría
    Actualizado para manejar Sub Categorías II y III
    """
    try:
        # Obtener el nombre de la categoría (cualquier nivel)
        categoria_nombre = ""
        tipificacion_nombre = ""
        
        if evaluacion.categoria:
            categoria_nombre = evaluacion.categoria.nombre.upper()
            # Intentar obtener la tipificación desde la categoría o directamente
            if hasattr(evaluacion.categoria, 'tipificacion') and evaluacion.categoria.tipificacion:
                tipificacion_nombre = evaluacion.categoria.tipificacion.nombre.upper()
            elif evaluacion.tipificacion:
                tipificacion_nombre = evaluacion.tipificacion.nombre.upper()
        elif evaluacion.tipificacion:
            tipificacion_nombre = evaluacion.tipificacion.nombre.upper()
        
        # Casos de alta prioridad
        palabras_alta_prioridad = [
            'VIOLENCIA', 'SEXUAL', 'INTRAFAMILIAR', 'MENOR', 'INFANTIL', 
            'HOMICIDIO', 'SECUESTRO', 'EXTORSIÓN', 'AMENAZA', 'URGENTE',
            'CRISIS', 'NNA'  # Agregadas para Sub Categorías II/III
        ]
        
        # Casos de baja prioridad  
        palabras_baja_prioridad = [
            'CONSULTA', 'INFORMACIÓN', 'ORIENTACIÓN', 'DOCUMENTOS', 'COPIA'
        ]
        
        texto_completo = f"{categoria_nombre} {tipificacion_nombre}"
        
        for palabra in palabras_alta_prioridad:
            if palabra in texto_completo:
                return 'ALTA'
                
        for palabra in palabras_baja_prioridad:
            if palabra in texto_completo:
                return 'BAJA'
                
        return 'MEDIA'  # Prioridad por defecto
        
    except Exception as e:
        print(f"Error determinando prioridad: {e}")
        return 'MEDIA'  # En caso de error, asignar prioridad media


@login_required
@en_grupo([Roles.ADMINISTRADOR.value, Roles.SUPERVISOR.value, Roles.AGENTE.value])
def buscar_tipificacion(request):
    """
    Busca Evaluacion(es) por número de identificación del ciudadano,
    correo/teléfono de contacto guardados en la Evaluación (anónimo),
    y correo/teléfono del Ciudadano (no anónimo / legacy).
    Paginadas de a 10. Devuelve todos los campos relacionados.
    """
    query = (request.GET.get('q') or '').strip()
    evaluaciones = Evaluacion.objects.none()
    paginator = None

    if query:
        qs = (
            Evaluacion.objects
            .select_related(
                'ciudadano__tipo_identificacion',
                'ciudadano__pais',
                'categoria__tipificacion',
                'categoria__categoria_padre',
                'user',
                'tipo_canal',
                'segmento',
                'segmento_ii',
                'segmento_iii',  
                'tipificacion'
            )
            .filter(
                Q(ciudadano__numero_identificacion__icontains=query) |
                Q(contacto_telefono__icontains=query) |
                Q(contacto_correo__icontains=query) |
                Q(contacto_telefono_inconcer__icontains=query) |
                Q(ciudadano__telefono__icontains=query) |
                Q(ciudadano__correo__icontains=query)
            )
            .order_by('-fecha')
        )

        paginator = Paginator(qs, 10)
        page_number = request.GET.get('page') or 1
        evaluaciones = paginator.get_page(page_number)

    return render(request, 'usuarios/evaluaciones/buscar_tipificacion.html', {
        'evaluaciones': evaluaciones,
        'paginator':    paginator,
        'page_obj':     evaluaciones,
        'is_paginated': evaluaciones.has_other_pages() if evaluaciones else False,
        'query':        query,
    })


def get_quick_range(quick: str):
    """
    quick ∈ {'hoy', 'ayer', '7d'}
    Retorna (start, end, etiqueta) como timezone-aware.
    - 'hoy'   : 00:00 de hoy → ahora
    - 'ayer'  : 00:00 de ayer → 00:00 de hoy (usaremos lt end)
    - '7d'    : ahora - 7 días → ahora
    """
    tz_now = now()
    if quick == 'hoy':
        start = tz_now.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = tz_now
        return start, end, 'hoy'
    if quick == 'ayer':
        ayer  = tz_now - timedelta(days=1)
        start = ayer.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = start + timedelta(days=1) 
        return start, end, 'ayer'
    if quick == '7d':
        start = tz_now - timedelta(days=7)
        end   = tz_now
        return start, end, '7d'
    return None, None, None



@login_required
@en_grupo([Roles.ADMINISTRADOR.value, Roles.SUPERVISOR.value, Roles.AGENTE.value])
def reportes_view(request):
    quick = request.GET.get('quick')  
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    usuario_id = request.GET.get('usuario')
    canal_id = request.GET.get('canal')

    qs = (
        Evaluacion.objects
        .select_related(
            'ciudadano__tipo_identificacion',
            'ciudadano__pais',
            'categoria__tipificacion',
            'categoria__categoria_padre',
            'user',
            'tipo_canal',
            'segmento',
            'segmento_ii',
            'tipificacion'
        )
        .order_by('-fecha')
    )

    if quick in ('hoy', 'ayer', '7d'):
        start, end, _ = get_quick_range(quick)
        if quick == 'ayer':
            qs = qs.filter(fecha__gte=start, fecha__lt=end)
        else:
            qs = qs.filter(fecha__range=(start, end))
    elif fecha_inicio and fecha_fin:
        try:
            fmt = '%Y-%m-%d'
            fi = make_aware(datetime.strptime(fecha_inicio, fmt))
            ff = make_aware(datetime.strptime(fecha_fin,    fmt))
            qs = qs.filter(fecha__range=(fi, ff))
        except ValueError:
            pass
    else:
        start, end, _ = get_quick_range('hoy')
        qs = qs.filter(fecha__range=(start, end))
        quick = 'hoy'

    if usuario_id and str(usuario_id).isdigit():
        qs = qs.filter(user_id=int(usuario_id))
    if canal_id and str(canal_id).isdigit():
        qs = qs.filter(tipo_canal_id=int(canal_id))

    usuarios = User.objects.filter(groups__name__in=['Agente', 'Supervisor', 'Administrador']).distinct()
    canales = TipoCanal.objects.all()
    
    base = Evaluacion.objects.all()
    if usuario_id and str(usuario_id).isdigit():
        base = base.filter(user_id=int(usuario_id))
    if canal_id and str(canal_id).isdigit():
        base = base.filter(tipo_canal_id=int(canal_id))

    hoy_start, hoy_end, _ = get_quick_range('hoy')
    ayer_start, ayer_end, _ = get_quick_range('ayer')
    semana_start, semana_end, _ = get_quick_range('7d')

    total_hoy = base.filter(fecha__range=(hoy_start, hoy_end)).count()
    total_ayer = base.filter(fecha__gte=ayer_start, fecha__lt=ayer_end).count()
    total_7d = base.filter(fecha__range=(semana_start, semana_end)).count()

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page') or 1)

    return render(request, 'usuarios/reportes.html', {
        'reportes': page_obj,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'hoy': now().date().isoformat(),
        'quick': quick,
        'usuarios': usuarios,
        'canales': canales,
        'total_hoy': total_hoy,
        'total_ayer': total_ayer,
        'total_7d': total_7d,
    })



def xl_safe(v):
    if v is None:
        return ''
    return ILLEGAL_CHARACTERS_RE.sub('', str(v))


@require_GET
@login_required
@en_grupo([Roles.ADMINISTRADOR.value, Roles.SUPERVISOR.value])
def exportar_excel(request):
    quick        = request.GET.get('quick')
    hoy_flag     = request.GET.get('hoy') == '1'
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin    = request.GET.get('fecha_fin')
    usuario      = request.GET.get('usuario')
    canal        = request.GET.get('canal')

    qs = (
        Evaluacion.objects
        .select_related(
            'ciudadano__tipo_identificacion',
            'ciudadano__pais',
            'categoria__tipificacion',
            'categoria__categoria_padre',
            'user',
            'tipo_canal',
            'segmento',
            'segmento_ii',
            'tipificacion',
            'abogado',
            'caso_abogado', 'caso_abogado__delito'
        )
        .order_by('-fecha')
    )

    if quick in ('hoy', 'ayer', '7d') or hoy_flag:
        use_quick = quick or 'hoy'
        start, end, _ = get_quick_range(use_quick)
        if use_quick == 'ayer':
            qs = qs.filter(fecha__gte=start, fecha__lt=end)
        else:
            qs = qs.filter(fecha__range=(start, end))
    elif fecha_inicio and fecha_fin:
        try:
            fmt = '%Y-%m-%d'
            fi = make_aware(datetime.strptime(fecha_inicio, fmt))
            ff = make_aware(datetime.strptime(fecha_fin,    fmt))
            qs = qs.filter(fecha__range=(fi, ff))
        except ValueError:
            pass
    else:
        if not (usuario and str(usuario).isdigit()) and not (canal and str(canal).isdigit()):
            start, end, _ = get_quick_range('hoy')
            qs = qs.filter(fecha__range=(start, end))

    if usuario and str(usuario).isdigit():
        qs = qs.filter(user_id=int(usuario))
    if canal and str(canal).isdigit():
        qs = qs.filter(tipo_canal_id=int(canal))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reportes"

    headers = [
        'Fecha', 'Tipo Documento', 'Número ID', 'Nombre',
        'Correo', 'Teléfono',
        'Correo contacto', 'Teléfono contacto', 'Teléfono Inconcer',  
        'País', 'Ciudad', 'Dirección',
        'ID Conversación', 'Tipo Canal', 'Segmento', 'Segmento II',
        'Tipificación', 'Categoría', 'Categoría Padre',
        'Sub Categoría II', 'Sub Categoría III', 'Nivel Final',
        'Cuál Otro Delito', 'Observación', 'Se comunica URI', 'Ciudad/Municipio URI', 'Consulta Jurídica',
        'Delito Código', 'Delito Nombre', 'Interacción Directa', 'Habeas Corpus',
        'Tutela', 'Observaciones Abogado', 'Fecha Tipificación Abogado', 'Estado de Caso',
        'Abogado', 'Usuario'
    ]
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)

    for row_idx, ev in enumerate(qs.iterator(), start=2):
        ciu = ev.ciudadano

        # === Fallback: primero Evaluación; si no, Ciudadano ===
        correo_base = ciu.correo or ''
        telf_base   = ciu.telefono or ''

        correo_contacto = ev.contacto_correo or ''
        telf_contacto   = ev.contacto_telefono or ''
        telf_inconser   = ev.contacto_telefono_inconcer or ''  # tal cual tu modelo

        # Flags legibles
        se_comunica_uri   = 'SÍ' if ev.se_comunica_uri is True else 'NO' if ev.se_comunica_uri is False else 'N/A'
        consulta_juridica = 'SÍ' if ev.consulta_juridica is True else 'NO' if ev.consulta_juridica is False else 'N/A'
        abogado_nombre    = ev.abogado.nombre if ev.abogado else ''

        caso_abogado = getattr(ev, 'caso_abogado', None)
        delito_codigo = caso_abogado.delito.codigo if caso_abogado and caso_abogado.delito else ''
        delito_nombre = caso_abogado.delito.nombre if caso_abogado and caso_abogado.delito else ''
        interaccion_directa = 'SÍ' if caso_abogado and caso_abogado.interaccion_directa_usuario is True else 'NO' if caso_abogado and caso_abogado.interaccion_directa_usuario is False else 'N/A'
        habeas_corpus = 'SÍ' if caso_abogado and caso_abogado.habeas_corpus is True else 'NO' if caso_abogado and caso_abogado.habeas_corpus is False else 'N/A'
        tutela = 'SÍ' if caso_abogado and caso_abogado.tutela is True else 'NO' if caso_abogado and caso_abogado.tutela is False else 'N/A'
        observaciones_abogado = caso_abogado.observaciones_abogado if caso_abogado else ''
        fecha_tipificacion_abogado = ''
        estado_caso = 'N/A'
        if caso_abogado:
            try:
                fecha_tipificacion_abogado = (
                    localtime(caso_abogado.fecha_tipificacion_agente).strftime('%Y-%m-%d %H:%M')
                    if caso_abogado.fecha_tipificacion_agente else 'Sin tipificar'
                )
            except Exception:
                fecha_tipificacion_abogado = 'Sin tipificar'
            try:
                estado_caso = caso_abogado.get_estado_display()
            except Exception:
                estado_caso = 'N/A'

        # === Jerarquía de categorías (igual que tu lógica actual) ===
        categoria_principal = ''
        categoria_padre_nombre = ''
        subcategoria_ii_nombre = ''
        subcategoria_iii_nombre = ''
        nivel_final = ''
        if ev.categoria:
            categoria_nivel = ev.categoria.nivel if hasattr(ev.categoria, 'nivel') else 1
            if categoria_nivel == 1:
                categoria_principal = ev.categoria.nombre
                nivel_final = 'Categoría'
            elif categoria_nivel == 2:
                categoria_principal    = ev.categoria.categoria_padre.nombre if ev.categoria.categoria_padre else ''
                categoria_padre_nombre = ev.categoria.nombre
                nivel_final = 'Sub Categoría'
            elif categoria_nivel == 3:
                subcategoria_ii_nombre = ev.categoria.nombre
                if ev.categoria.categoria_padre:
                    categoria_padre_nombre = ev.categoria.categoria_padre.nombre
                    categoria_principal    = ev.categoria.categoria_padre.categoria_padre.nombre if ev.categoria.categoria_padre.categoria_padre else ''
                nivel_final = 'Sub Categoría II'
            elif categoria_nivel == 4:
                subcategoria_iii_nombre = ev.categoria.nombre
                if ev.categoria.categoria_padre:
                    subcategoria_ii_nombre = ev.categoria.categoria_padre.nombre
                    if ev.categoria.categoria_padre.categoria_padre:
                        categoria_padre_nombre = ev.categoria.categoria_padre.categoria_padre.nombre
                        categoria_principal = (
                            ev.categoria.categoria_padre.categoria_padre.categoria_padre.nombre
                            if ev.categoria.categoria_padre.categoria_padre.categoria_padre else ''
                        )
                nivel_final = 'Sub Categoría III'
            else:
                categoria_principal = ev.categoria.nombre
                nivel_final = f'Nivel {categoria_nivel}'
        else:
            categoria_principal = 'Sin categoría específica'
            nivel_final = 'Sin categoría'

        # === Ordena las columnas según headers (incluyendo las 3 nuevas) ===
        data = [
            localtime(ev.fecha).strftime('%Y-%m-%d %H:%M'),
            ciu.tipo_identificacion.nombre,
            ciu.numero_identificacion,
            ciu.nombre,
            correo_base,
            telf_base,
            correo_contacto,
            telf_contacto,
            telf_inconser,
            ciu.pais.nombre if ciu.pais else '',
            ciu.ciudad or '',
            ciu.direccion_residencia or '',
            ev.conversacion_id,
            ev.tipo_canal.nombre if ev.tipo_canal else '',
            ev.segmento.nombre if ev.segmento else '',
            ev.segmento_ii.nombre if ev.segmento_ii else '',
            ev.tipificacion.nombre if ev.tipificacion else '',
            categoria_principal,
            categoria_padre_nombre,
            subcategoria_ii_nombre,
            subcategoria_iii_nombre,
            nivel_final,
            ev.cual_otro_delito or '',
            ev.observacion,
            se_comunica_uri,
            ev.ciudad_municipio_uri or '',
            consulta_juridica,
            delito_codigo,
            delito_nombre,
            interaccion_directa,
            habeas_corpus,
            tutela,
            observaciones_abogado,
            fecha_tipificacion_abogado,
            estado_caso,
            abogado_nombre,
            ev.user.username
        ]
        for col, value in enumerate(data, 1):
            ws.cell(row=row_idx, column=col, value=xl_safe(value))

    # Auto-anchos (con límite)
    col_widths = [len(h) + 2 for h in headers]
    for r in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(headers)):
        for i, cell in enumerate(r):
            val = '' if cell.value is None else str(cell.value)
            w = len(val) + 2
            if w > col_widths[i]:
                col_widths[i] = min(w, 60)
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = max(12, w)

    # Guardar y responder
    buffer = BytesIO()
    try:
        wb.save(buffer)
    except Exception as e:
        RegistrarError('exportar_excel', str(e), request)
        messages.error(request, 'No se pudo generar el Excel. Soporte ha sido notificado.')
        return redirect('reportes_view')

    buffer.seek(0)
    resp = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    resp['Content-Disposition'] = 'attachment; filename="reportes_tipificaciones.xlsx"'
    return resp