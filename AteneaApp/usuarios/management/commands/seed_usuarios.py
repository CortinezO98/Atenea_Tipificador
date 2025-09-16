import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.db import transaction
from usuarios.management.data.users import users
from usuarios.enums import Roles

class Command(BaseCommand):
    help = 'Carga datos de prueba en la base de datos'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.stdout.write("🔧 Creando roles…")
                self.create_roles()
                self.stdout.write("👤 Creando usuarios…")
                self.create_users()
            self.stdout.write(self.style.SUCCESS('✅ Datos creados correctamente.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error, se hizo rollback: {e}"))

    def create_roles(self):
        for role in [Roles.ADMINISTRADOR, Roles.SUPERVISOR, Roles.AGENTE, Roles.ABOGADO]:
            Group.objects.get_or_create(
                id=role.value,
                defaults={'name': role.label}
            )

    def create_users(self):
        for userData in users:
            user = User.objects.filter(username=userData['username']).first()
            if not user:
                user = User.objects.create_user(
                    username    = userData['username'],
                    password    = userData['password'],
                    is_staff    = userData['is_staff'],
                    is_superuser= userData['is_superuser'],
                    first_name  = userData.get('first_name', ''),
                    last_name   = userData.get('last_name', ''),
                    email       = userData.get('email', ''),
                )
                group = Group.objects.filter(id=userData['role_id']).first()
                if group:
                    user.groups.add(group)
                    self.stdout.write(f"   ✅ Usuario creado: {user.username} → {group.name}")
            else:
                self.stdout.write(f"   ⚠️ Usuario ya existe: {user.username}")
