from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import *
from django.http import HttpResponse
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import *
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.utils.timezone import make_aware
from django.utils.timezone import now, localtime
from django.db.models import Count
from datetime import datetime
from django.shortcuts import redirect
from .enums import Roles
from gestion.utils import RegistrarError
from gestion.models import *
import inspect

def home_redirect_view(request):
    if request.user.is_authenticated:
        return redirect('home')  
    else:
        return render(request, 'usuarios/auth/login.html')


def en_grupo(roles_id):
    def check(user):
        for rol_id in roles_id:
            if user.groups.filter(id=rol_id).exists():
                return True
    return user_passes_test(check)


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Credenciales incorrectas. Intenta nuevamente.")
        else:
            messages.error(request, "Captcha incorrecto. Intenta nuevamente.")
    return render(request, 'usuarios/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@en_grupo([Roles.AGENTE.value])
def dashboard_agente(request):
    query = request.GET.get('q', '').strip()
    qs = Evaluacion.objects.filter(user=request.user).select_related('ciudadano', 'categoria')

    if query:
        qs = qs.filter(ciudadano__numero_identificacion__icontains=query)

    qs = qs.order_by('-fecha')
    paginator = Paginator(qs, 10)
    page_num = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_num)

    return render(request, 'usuarios/dashboard_agente.html', {
        'evaluaciones': page_obj,
        'paginator':    paginator,
        'page_obj':     page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query':        query,
    })


@login_required
@en_grupo([Roles.SUPERVISOR.value])
def dashboard_supervisor(request):
    hoy = timezone.localdate()

    total_evaluaciones = Evaluacion.objects.count()
    evaluaciones_hoy   = Evaluacion.objects.filter(fecha__date=hoy).count()

    agentes_activos = User.objects.filter(
        is_active=True,
        groups__name=Roles.AGENTE.label
    ).count()


    if agentes_activos > 0:
        eficiencia = round((evaluaciones_hoy / agentes_activos) * 100, 1)
    else:
        eficiencia = 0.0

    actividad_reciente = (
        Evaluacion.objects
        .select_related('ciudadano', 'categoria', 'categoria__tipificacion', 'categoria__categoria_padre', 'user')
        .order_by('-fecha')[:5]
    )

    context = {
        'total_evaluaciones': total_evaluaciones,
        'evaluaciones_hoy':   evaluaciones_hoy,
        'agentes_activos':    agentes_activos,
        'eficiencia':         eficiencia,
        'actividad_reciente': actividad_reciente,
    }
    return render(request, 'usuarios/dashboard_supervisor.html', context)


@login_required
@en_grupo([Roles.ADMINISTRADOR.value])
def dashboard_admin(request):
    return render(request, 'usuarios/dashboard_admin.html')


@login_required
@en_grupo([Roles.ADMINISTRADOR.value])
def crear_usuario(request, user_id=None):
    user = get_object_or_404(User, id=user_id) if user_id else None
    grupos = Group.objects.filter(id__in=[Roles.ADMINISTRADOR.value,Roles.SUPERVISOR.value,Roles.AGENTE.value,Roles.ABOGADO.value,])
    grupo_asignado = user.groups.first() if user else None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        rol_id = request.POST.get("rol", "")
        is_active = request.POST.get("is_active") == "on"

        errors = []
        
        required_fields = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'rol': rol_id
        }
        
        if not user: 
            required_fields['password'] = password
            required_fields['confirm_password'] = confirm_password

        for field, value in required_fields.items():
            if not value:
                errors.append(f"El campo {field.replace('_', ' ')} es requerido.")

        if password or confirm_password:
            if password != confirm_password:
                errors.append("Las contraseñas no coinciden.")
            elif len(password) < 8:
                errors.append("La contraseña debe tener al menos 8 caracteres.")

        if User.objects.filter(username=username).exclude(pk=user.pk if user else None).exists():
            errors.append("El nombre de usuario ya está en uso.")
            
        if User.objects.filter(email=email).exclude(pk=user.pk if user else None).exists():
            errors.append("El correo electrónico ya está en uso.")

        if email and '@' not in email:
            errors.append("Ingrese un correo electrónico válido.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'usuarios/auth/crear_usuario.html', {
                'user': user,
                'grupos': grupos,
                'grupo_asignado': grupo_asignado
            })

        try:
            grupo = Group.objects.get(id=rol_id)
            
            if not user:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=is_active
                )
            else:
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = is_active
                if password:
                    user.set_password(password)
                user.save()

            user.groups.clear()
            user.groups.add(grupo)

            if int(rol_id) == Roles.ABOGADO.value:
                nombre_completo = f"{user.first_name} {user.last_name}".strip() or user.username
                Abogado.objects.update_or_create(
                    email=user.email,
                    defaults={'nombre': nombre_completo}
                )
            
            grupo_nombre = grupo.name.lower()

            messages.success(request, f"Usuario {'actualizado' if user_id else 'creado'} correctamente.")
            return redirect('dashboard_admin')

        except Exception as e:
            RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
            messages.error(request, f"Error al {'actualizar' if user_id else 'crear'} el usuario")
            return render(request, 'usuarios/auth/crear_usuario.html', {
                'user': user,
                'grupos': grupos,
                'grupo_asignado': grupo_asignado
            })

    return render(request, 'usuarios/auth/crear_usuario.html', {
        'user': user,
        'grupos': grupos,
        'grupo_asignado': grupo_asignado
    })


@login_required
@en_grupo([Roles.ADMINISTRADOR.value])
def ver_usuarios(request):
    query = request.GET.get('q', '').strip()
    usuarios_list = User.objects.all().order_by('username')

    if query:
        search_terms = query.split()
        q_objects = Q()
        for term in search_terms:
            q_objects |= Q(username__icontains=term)
            q_objects |= Q(first_name__icontains=term)
            q_objects |= Q(last_name__icontains=term)
            q_objects |= Q(email__icontains=term)
        usuarios_list = usuarios_list.filter(q_objects).distinct()

    page = request.GET.get('page', 1)
    paginator = Paginator(usuarios_list, 10)  

    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)

    context = {
        'usuarios': usuarios,
        'query': query,
        'paginator': paginator,
        'start_index': usuarios.start_index(),
        'end_index': usuarios.end_index(),
    }

    return render(request, 'usuarios/auth/ver_usuarios.html', context)


@login_required
@en_grupo([Roles.ADMINISTRADOR.value])
@require_POST
def toggle_user_status(request, user_id):
    try:
        usuario = User.objects.get(id=user_id)
        usuario.is_active = not usuario.is_active
        usuario.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@en_grupo([Roles.ADMINISTRADOR.value])
def eliminar_usuario(request, user_id):
    try:
        usuario = User.objects.get(id=user_id)
        usuario.delete()
        messages.success(request, f'Usuario {usuario.username} eliminado correctamente')
        return redirect('ver_usuarios')
    except User.DoesNotExist:
        messages.error(request, 'El usuario no existe')
        return redirect('ver_usuarios')
    except Exception as e:
        RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
        messages.error(request, f'Error al eliminar usuario: {str(e)}')
        return redirect('ver_usuarios')


@login_required
@en_grupo([Roles.ADMINISTRADOR.value])
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name', usuario.first_name)
        usuario.last_name = request.POST.get('last_name', usuario.last_name)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente')
        return redirect('ver_usuarios')

    return render(request, 'usuarios/editar_usuario.html', {'usuario': usuario})


def ValidarRolUsuario(request, rol_id):
    user = request.user
    return user.groups.filter(id=rol_id).exists()

@login_required
@en_grupo([Roles.ABOGADO.value])
def dashboard_abogado(request):
    try:
        abogado = Abogado.objects.filter(
            models.Q(email=request.user.email) | 
            models.Q(nombre__icontains=request.user.get_full_name())
        ).first()
        
        if not abogado:
            messages.warning(request, "No se encontró su perfil de abogado. Contacte al administrador.")
            return redirect('logout')
            
        casos_pendientes = CasoAbogado.objects.filter(abogado=abogado, estado='PENDIENTE').count()
        casos_en_revision = CasoAbogado.objects.filter(abogado=abogado, estado='EN_REVISION').count()
        casos_completados = CasoAbogado.objects.filter(abogado=abogado, estado='COMPLETADO').count()
        total_casos = CasoAbogado.objects.filter(abogado=abogado).count()
        
        casos_recientes = (
            CasoAbogado.objects
            .filter(abogado=abogado)
            .select_related(
                'evaluacion__ciudadano__tipo_identificacion',
                'evaluacion__tipificacion',  
                'evaluacion__categoria',    
                'evaluacion__user'
            )
            .order_by('-fecha_asignacion')[:10]
        )
        
        context = {
            'abogado': abogado,
            'casos_pendientes': casos_pendientes,
            'casos_en_revision': casos_en_revision,
            'casos_completados': casos_completados,
            'total_casos': total_casos,
            'casos_recientes': casos_recientes,
        }
        
        return render(request, 'usuarios/dashboard_abogado.html', context)
        
    except Exception as e:
        print(f"ERROR en dashboard_abogado: {e}")
        import traceback
        traceback.print_exc()
        RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
        messages.error(request, "Error al cargar el dashboard.")
        return redirect('logout')


@login_required  
@en_grupo([Roles.ABOGADO.value])
def mis_casos_abogado(request):
    try:
        abogado = Abogado.objects.filter(
            models.Q(email=request.user.email) | 
            models.Q(nombre__icontains=request.user.get_full_name())
        ).first()
        
        if not abogado:
            messages.warning(request, "No se encontró su perfil de abogado.")
            return redirect('logout')
        
        print(f"DEBUG: Abogado encontrado: {abogado.nombre}")
        
        estado_filtro = request.GET.get('estado', '')
        prioridad_filtro = request.GET.get('prioridad', '')
        busqueda = request.GET.get('q', '')
        
        casos_qs = (
            CasoAbogado.objects
            .filter(abogado=abogado)
            .select_related(
                'evaluacion__ciudadano__tipo_identificacion',
                'evaluacion__tipificacion',  
                'evaluacion__categoria',     
                'evaluacion__user'
            )
        )
        
        print(f"DEBUG: Casos base encontrados: {casos_qs.count()}")
        
        if estado_filtro:
            casos_qs = casos_qs.filter(estado=estado_filtro)
            
        if prioridad_filtro:
            casos_qs = casos_qs.filter(prioridad=prioridad_filtro)
            
        if busqueda:
            casos_qs = casos_qs.filter(
                models.Q(evaluacion__ciudadano__nombre__icontains=busqueda) |
                models.Q(evaluacion__ciudadano__numero_identificacion__icontains=busqueda) |
                models.Q(evaluacion__tipificacion__nombre__icontains=busqueda) 
            )
        
        casos_qs = casos_qs.order_by('-fecha_asignacion')
        
        print(f"DEBUG: Casos después de filtros: {casos_qs.count()}")
        
        # Paginación
        paginator = Paginator(casos_qs, 15)
        page_num = request.GET.get('page') or 1
        page_obj = paginator.get_page(page_num)
        
        print(f"DEBUG: Casos en página actual: {len(page_obj)}")

        estados_filtrados = [
            (value, label) for value, label in CasoAbogado.ESTADO_CHOICES 
            if value != 'COMPLETADO'
        ]
        
        context = {
            'casos': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'estado_filtro': estado_filtro,
            'prioridad_filtro': prioridad_filtro,
            'busqueda': busqueda,
            'abogado': abogado,
            # 'estados_choices': CasoAbogado.ESTADO_CHOICES,
            'estados_choices': estados_filtrados,
            'prioridades_choices': CasoAbogado.PRIORIDAD_CHOICES,
        }
        
        return render(request, 'usuarios/casos/mis_casos_abogado.html', context)
        
    except Exception as e:
        print(f"ERROR en mis_casos_abogado: {e}")
        import traceback
        traceback.print_exc()
        RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
        messages.error(request, "Error al cargar los casos.")
        return redirect('dashboard_abogado')


@login_required
@en_grupo([Roles.ABOGADO.value])
def detalle_caso_abogado(request, caso_id):
    try:
        abogado = Abogado.objects.filter(
            models.Q(email=request.user.email) | 
            models.Q(nombre__icontains=request.user.get_full_name())
        ).first()
        
        if not abogado:
            messages.warning(request, "No se encontró su perfil de abogado.")
            return redirect('logout')
        
        caso = get_object_or_404(
            CasoAbogado.objects.select_related(
                'evaluacion__ciudadano__tipo_identificacion',
                'evaluacion__ciudadano__pais',
                'evaluacion__tipificacion',       
                'evaluacion__categoria__categoria_padre',  
                'evaluacion__user'
            ),
            id=caso_id,
            abogado=abogado
        )
        
        print(f"DEBUG: Caso encontrado: {caso.id}")
        print(f"DEBUG: Ciudadano: {caso.evaluacion.ciudadano.nombre}")
        print(f"DEBUG: Tipificación: {caso.evaluacion.tipificacion.nombre}")
        
        if request.method == 'POST':
            es_primera_actualizacion = not caso.fecha_tipificacion_agente
            caso.estado = request.POST.get('estado', caso.estado)
            caso.prioridad = request.POST.get('prioridad', caso.prioridad)
            caso.observaciones_abogado = request.POST.get('observaciones_abogado', '')
            
            # Campos jurídicos
            delito_id = request.POST.get('delito')
            if delito_id:
                try:
                    caso.delito = Delito.objects.get(id=delito_id)
                except Delito.DoesNotExist:
                    caso.delito = None
            else:
                caso.delito = None
            
            # Interacción directa
            interaccion_directa = request.POST.get('interaccion_directa_usuario')
            if interaccion_directa == '1':
                caso.interaccion_directa_usuario = True
            elif interaccion_directa == '0':
                caso.interaccion_directa_usuario = False
            else:
                caso.interaccion_directa_usuario = None
            
            # Habeas Corpus
            habeas_corpus = request.POST.get('habeas_corpus')
            if habeas_corpus == '1':
                caso.habeas_corpus = True
            elif habeas_corpus == '0':
                caso.habeas_corpus = False
            else:
                caso.habeas_corpus = None
            
            # Tutela
            tutela = request.POST.get('tutela')
            if tutela == '1':
                caso.tutela = True
            elif tutela == '0':
                caso.tutela = False
            else:
                caso.tutela = None

            if es_primera_actualizacion and (caso.observaciones_abogado or caso.delito or 
                                           caso.interaccion_directa_usuario is not None or 
                                           caso.habeas_corpus is not None or 
                                           caso.tutela is not None):
                caso.fecha_tipificacion_agente = timezone.now()
                print(f"DEBUG: Primera tipificación del abogado registrada: {caso.fecha_tipificacion_agente}")    
            
            if caso.estado == 'EN_REVISION' and not caso.fecha_revision:
                caso.fecha_revision = timezone.now()
            elif caso.estado == 'COMPLETADO' and not caso.fecha_completado:
                caso.fecha_completado = timezone.now()
            
            caso.save()
            messages.success(request, "Caso actualizado correctamente.")
            return redirect('detalle_caso_abogado', caso_id=caso.id)
        
        delitos = Delito.objects.filter(activo=True).order_by('codigo', 'nombre')

        estados_filtrados = [
            (value, label) for value, label in CasoAbogado.ESTADO_CHOICES 
            if value != 'COMPLETADO'
        ]
        
        context = {
            'caso': caso,
            'abogado': abogado,
            # 'estados_choices': CasoAbogado.ESTADO_CHOICES,
            'estados_choices': estados_filtrados,
            'prioridades_choices': CasoAbogado.PRIORIDAD_CHOICES,
            'delitos': delitos,
        }
        
        return render(request, 'usuarios/casos/detalle_caso_abogado.html', context)
        
    except Exception as e:
        print(f"ERROR en detalle_caso_abogado: {e}")
        import traceback
        traceback.print_exc()
        RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
        messages.error(request, "Error al cargar el caso.")
        return redirect('mis_casos_abogado')


@login_required
@en_grupo([Roles.ABOGADO.value])
def buscar_casos_abogado(request):
    try:
        abogado = Abogado.objects.filter(
            models.Q(email=request.user.email) | 
            models.Q(nombre__icontains=request.user.get_full_name())
        ).first()
        
        if not abogado:
            messages.warning(request, "No se encontró su perfil de abogado.")
            return redirect('logout')
        
        casos = CasoAbogado.objects.none()
        
        if request.GET:
            casos_qs = (
                CasoAbogado.objects
                .filter(abogado=abogado)
                .select_related(
                    'evaluacion__ciudadano__tipo_identificacion',
                    'evaluacion__tipificacion',  
                    'evaluacion__categoria',     
                    'evaluacion__user'
                )
            )
            
            # Filtros avanzados
            numero_documento = request.GET.get('numero_documento', '').strip()
            estado = request.GET.get('estado', '')
            prioridad = request.GET.get('prioridad', '')
            fecha_desde = request.GET.get('fecha_desde', '')
            fecha_hasta = request.GET.get('fecha_hasta', '')
            
            if numero_documento:
                casos_qs = casos_qs.filter(
                    evaluacion__ciudadano__numero_identificacion__icontains=numero_documento
                )
            
            if estado:
                casos_qs = casos_qs.filter(estado=estado)
                
            if prioridad:
                casos_qs = casos_qs.filter(prioridad=prioridad)
                
            if fecha_desde:
                try:
                    fecha_desde_dt = make_aware(datetime.strptime(fecha_desde, '%Y-%m-%d'))
                    casos_qs = casos_qs.filter(fecha_asignacion__gte=fecha_desde_dt)
                except ValueError:
                    pass
                    
            if fecha_hasta:
                try:
                    fecha_hasta_dt = make_aware(datetime.strptime(fecha_hasta, '%Y-%m-%d'))
                    casos_qs = casos_qs.filter(fecha_asignacion__lte=fecha_hasta_dt)
                except ValueError:
                    pass
            
            casos_qs = casos_qs.order_by('-fecha_asignacion')
            
            # Paginación
            paginator = Paginator(casos_qs, 10)
            page_num = request.GET.get('page') or 1
            casos = paginator.get_page(page_num)

        estados_filtrados = [
            (value, label) for value, label in CasoAbogado.ESTADO_CHOICES 
            if value != 'COMPLETADO'
        ]   
        
        context = {
            'casos': casos,
            'abogado': abogado,
            # 'estados_choices': CasoAbogado.ESTADO_CHOICES,
            'estados_choices': estados_filtrados,
            'prioridades_choices': CasoAbogado.PRIORIDAD_CHOICES,
        }
        
        return render(request, 'usuarios/casos/buscar_casos_abogado.html', context)
        
    except Exception as e:
        print(f"ERROR en buscar_casos_abogado: {e}")
        import traceback
        traceback.print_exc()
        RegistrarError(inspect.currentframe().f_code.co_name, str(e), request)
        messages.error(request, "Error en la búsqueda.")
        return redirect('dashboard_abogado')
