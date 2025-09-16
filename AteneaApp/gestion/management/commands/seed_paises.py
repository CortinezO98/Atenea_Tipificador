from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import Pais

class Command(BaseCommand):
    help = 'Carga países en la base de datos'

    def handle(self, *args, **kwargs):
        paises = [
            'Colombia',
            'Argentina',
            'Brasil',
            'Chile',
            'Perú',
            'Ecuador',
            'Bolivia',
            'Paraguay',
            'Uruguay',
            'Venezuela',
            'México',
            'Estados Unidos',
            'Canadá',
            'España',
            'Francia',
            'Italia',
            'Alemania',
            'Reino Unido',
            'Portugal',
            'Países Bajos',
            'Bélgica',
            'Suiza',
            'Austria',
            'Suecia',
            'Noruega',
            'Dinamarca',
            'Finlandia',
            'Rusia',
            'China',
            'Japón',
            'Corea del Sur',
            'India',
            'Australia',
            'Nueva Zelanda',
            'Sudáfrica',
            'Egipto',
            'Marruecos',
            'Nigeria',
            'Kenia',
            'Ghana',
        ]
        
        try:
            with transaction.atomic():
                paises_creados = 0
                paises_existentes = 0
                
                for nombre_pais in paises:
                    pais, created = Pais.objects.get_or_create(
                        nombre=nombre_pais
                    )
                    
                    if created:
                        paises_creados += 1
                        self.stdout.write(f"✅ Creado: {nombre_pais}")
                    else:
                        paises_existentes += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"🌍 Proceso completado!\n"
                        f"   📝 Países creados: {paises_creados}\n"
                        f"   ♻️  Países ya existían: {paises_existentes}\n"
                        f"   📊 Total países en BD: {Pais.objects.count()}"
                    )
                )
                
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Error al cargar países: {e}")
            )