from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from gestion.models import TipoIdentificacion
from gestion.management.data.tiposIdentificacion import tiposIdentificacion

class Command(BaseCommand):
    help = "Carga SOLO lo mínimo requerido: Tipos de Identificación, Países y Niveles (N1..N6)."

    @transaction.atomic
    def handle(self, *args, **options):
        creados_tipos = 0
        existentes_tipos = 0

        # 1) Tipos de Identificación (obligatorio para tu modelo)
        for item in tiposIdentificacion:
            obj, created = TipoIdentificacion.objects.get_or_create(
                id=item["id"],
                defaults={"nombre": item["nombre"]}
            )
            if not created and obj.nombre != item["nombre"]:
                obj.nombre = item["nombre"]
                obj.save(update_fields=["nombre"])
            if created:
                creados_tipos += 1
            else:
                existentes_tipos += 1

        self.stdout.write(self.style.SUCCESS(
            f"Tipos de Identificación -> creados: {creados_tipos} | existentes: {existentes_tipos}"
        ))

        # 2) Países
        self.stdout.write(self.style.NOTICE("Cargando países..."))
        call_command('seed_paises')  # usa tu comando existente

        # 3) Niveles (N1..N6)
        self.stdout.write(self.style.NOTICE("Cargando niveles (N1..N6)..."))
        call_command('seed_niveles')  # usa tu comando existente

        self.stdout.write(self.style.SUCCESS("✅ Seed mínimo completado."))
