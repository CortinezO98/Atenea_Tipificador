from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import *
from django.utils.translation import gettext_lazy as _


class AdminRestrict(AdminSite):
    site_header = "Panel Administrativo de Fiscalía"
    site_title = "Administración"
    index_title = "Bienvenido al Panel"

    def has_permission(self, request):
        """Permite el acceso solo a usuarios autenticados en el grupo 'administrador'."""
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='administrador').exists()
        )


admin_site = AdminRestrict(name='admin')






# Ejemplo de cómo registrar tus modelos con el nuevo sitio admin:
# from .models import TuModelo
# admin_site.register(TuModelo)
