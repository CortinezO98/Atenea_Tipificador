from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from usuarios.enums import Roles

class Command(BaseCommand):
    help = 'Añade el rol de Abogado a usuarios existentes sin modificar sus otros grupos'

    def handle(self, *args, **options):
        # Lista de usuarios a los que queremos agregar el rol de Abogado
        usernames = [
            '1032464988',  # Julián Hernando Navarrete Rodríguez
            '1012453558',  # Carol Daniela Meneses Fonseca
            '1016074186',  # Santiago Sánchez Leon
            '1013647181',  # Angie Alejandra Torres Quevedo
        ]

        with transaction.atomic():
            # Obtenemos (o aseguramos) el grupo Abogado
            abogado_group, created = Group.objects.get_or_create(
                id=Roles.ABOGADO.value,
                defaults={'name': Roles.ABOGADO.label}
            )
            if created:
                self.stdout.write(f'✅ Grupo “{abogado_group.name}” creado (id={abogado_group.id})')
            else:
                self.stdout.write(f'🔄 Grupo “{abogado_group.name}” ya existía (id={abogado_group.id})')

            # Para cada usuario, simplemente añadimos el grupo Abogado
            for username in usernames:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    self.stderr.write(f'⚠️  Usuario no encontrado: {username}')
                    continue

                if abogado_group in user.groups.all():
                    self.stdout.write(f'ℹ️  El usuario {username} ya tiene el rol de Abogado')
                else:
                    user.groups.add(abogado_group)
                    self.stdout.write(f'✔️   Añadido rol Abogado a {username}')

        self.stdout.write(self.style.SUCCESS('🎉 Rol de Abogado agregado a los usuarios indicados.'))
