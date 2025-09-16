from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import TipoCanal
from gestion.management.data.tiposCanal import tiposCanal

class Command(BaseCommand):
    help = 'Carga solo los tipos de canal (temporal para migración)'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                for tipoCanalData in tiposCanal:
                    tipoCanal = TipoCanal.objects.filter(id=tipoCanalData['id']).first()
                    if not tipoCanal:
                        TipoCanal.objects.create(
                            id=tipoCanalData['id'],
                            nombre=tipoCanalData['nombre']
                        )
                        self.stdout.write(f"✅ Creado: {tipoCanalData['nombre']}")
                    else:
                        self.stdout.write(f"⚠️ Ya existe: {tipoCanalData['nombre']}")
                        
                self.stdout.write(
                    self.style.SUCCESS('TipoCanal cargados correctamente.')
                )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Error: {e}")
            )