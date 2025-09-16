from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import Abogado

class Command(BaseCommand):
    help = 'Carga abogados de ejemplo en la base de datos'

    def handle(self, *args, **kwargs):
        abogados_data = [
            {
                'nombre': 'Angie Alejandra Torres Quevedo',
                'email': 'aleqtorres24@gmail.com',
                'telefono': '+57 301 234 5678',
                'especialidad': 'Derecho Penal'
            },
            {
                'nombre': 'Julian Hernando Navarrete Rodríguez',
                'email': 'julian.n2207@hotmail.com',
                'telefono': '+57 312 987 6543',
                'especialidad': 'Derecho Civil'
            },
            {
                'nombre': 'Carol Daniela Meneses Fonseca',
                'email': 'ardfonseca8c2012@gmail.com',
                'telefono': '+57 320 456 7890',
                'especialidad': 'Derecho Administrativo'
            },
            {
                'nombre': 'Santiago Sanchez Leon',
                'email': 'Leoned799@gmail.com',
                'telefono': '+57 315 654 3210',
                'especialidad': 'Derecho Laboral'
            }
        ]

        try:
            with transaction.atomic():
                for abogado_data in abogados_data:
                    abogado, created = Abogado.objects.get_or_create(
                        nombre=abogado_data['nombre'],
                        defaults=abogado_data
                    )
                    if created:
                        self.stdout.write(f"✅ Abogado creado: {abogado.nombre}")
                    else:
                        self.stdout.write(f"⚠️ Abogado ya existe: {abogado.nombre}")
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Proceso completado. Total abogados en BD: {Abogado.objects.count()}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )