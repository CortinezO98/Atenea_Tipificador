from django import template

register = template.Library()

@register.filter
def validarRolUsuario(user, roles_id_str):
    roles_id = [int(rol) for rol in roles_id_str.split('|')]
    for rol_id in roles_id:
        if user.groups.filter(id=rol_id).exists():
            return True
    return False