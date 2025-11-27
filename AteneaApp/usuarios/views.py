from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import *
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from .models import *
from django.utils import timezone
from django.utils.timezone import make_aware, now, localtime
from datetime import datetime
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
    """
    Decorador de autorización por grupo/rol.
    Se mantiene para compatibilidad, pero se refuerza con ValidarRolUsuario
    dentro de las vistas sensibles (defensa en profundidad).
    """
    def check(user):
        for rol_id in roles_id:
            if user.groups.filter(id=rol_id).exists():
                return True
        # Respuesta explícita para usuarios no autorizados
        return False

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
    """
    Dashboard del agente.
    - Control de función: sólo usuarios con rol AGENTE.
    - Control de objeto: sólo ve Evaluaciones asociadas a request.user.
    """
    if not ValidarRolUsuario(request, Roles.AGENTE.value):
        return HttpResponseForbidden("No autorizado")

    query = request.GET.get('q', '').strip()
    qs = (
        Evaluacion.objects
        .filter(user=request.user) 
        .select_related('ciudadano', 'categoria')
    )

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
    """
    Dashboard del supervisor.
    - Control de función: sólo usuarios con rol SUPERVISOR.
    - A nivel de negocio, el supervisor sí puede ver métricas globales.
    """
    if not ValidarRolUsuario(request, Roles.SUPERVISOR.value):
        return HttpResponseForbidden("No autorizado")

    hoy = timezone.localdate()

    total_evaluaciones = Evaluacion.objects.count()
    evaluaciones_hoy = Evaluacion.objects.filter(fecha__date=hoy).count()

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
        .select_related(
            'ciudadano',
            'categoria',
            'categoria__tipificacion',
            'categoria__categoria_padre',
            'user'
        )
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
    """
    Dashboard del administrador.
    - Control de función: sólo usuarios con rol ADMINISTRADOR.
    """
    if not ValidarRolUsuario(request, Roles.ADMINISTRADOR.value):
        return HttpResponseForbidden("No autorizado")

    return render(request, 'usuarios/dashboard_admin.html')


@login_required
@en_grupo([Roles.ADMINISTRADOR.value])
def crear_usuario(request, user_id=None):
    """
    Creación / edición de usuarios.
    - Control de función: sólo ADMINISTRADOR.
    """
    if not ValidarRolUsuario(request, Roles.ADMINISTRADOR.value):
        return HttpResponseForbidden("No autorizado")

    user = get_object_or_404(User, id=user_id) if user_id else None
    grupos = Group.objects.filter(
        id__in=[
            Roles.ADMINISTRADOR.value,
            Roles.SUPERVISOR.value,
            Roles.AGENTE.value,
            Roles.ABOGADO.value,
        ]
    )
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
    """
    Listado de usuarios.
    - Control de función: sólo ADMINISTRADOR.
    """
    if not ValidarRolUsuario(request, Roles.ADMINISTRADOR.value):
        return HttpResponseForbidden("No autorizado")

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
    """
    Activar/Desactivar usuario.
    - Control de función: sólo ADMINISTRADOR.
    - Control de objeto: se valida el rol del solicitante antes de modificar el estado del usuario objetivo.
    """
    if not ValidarRolUsuario(request, Roles.ADMINISTRADOR.value):
        return JsonResponse({'success': False, 'message': 'No autorizado'}, status=403)

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
    """
    Eliminación de usuario.
    - Control de función: sólo ADMINISTRADOR.
    """
    if not ValidarRolUsuario(request, Roles.ADMINISTRADOR.value):
        return HttpResponseForbidden("No autorizado")

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
    """
    Edición básica de datos de usuario.
    - Control de función: sólo ADMINISTRADOR.
    """
    if not ValidarRolUsuario(request, Roles.ADMINISTRADOR.value):
        return HttpResponseForbidden("No autorizado")

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
    """
    Función centralizada para validar si el usuario autenticado
    pertenece a un grupo/rol concreto.
    Se utiliza dentro de las vistas como refuerzo de seguridad
    (además de los decoradores) para cumplir con las buenas prácticas
    y satisfacer las reglas de SAST (Checkmarx).
    """
    user = request.user
    return user.is_authenticated and user.groups.filter(id=rol_id).exists()
