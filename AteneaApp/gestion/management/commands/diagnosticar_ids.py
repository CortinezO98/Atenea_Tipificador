from django.core.management.base import BaseCommand
from gestion.models import *

class Command(BaseCommand):
    help = 'Diagnostica diferencias entre IDs actuales y nuevos'
    
    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNÓSTICO DE IDs ===")
        
        # Ver Tipos Canal actuales
        self.stdout.write("\n📡 TIPOS CANAL ACTUALES:")
        for tc in TipoCanal.objects.all():
            self.stdout.write(f"  ID {tc.id}: {tc.nombre}")
        
        # Ver Segmentos actuales
        self.stdout.write("\n📊 SEGMENTOS ACTUALES:")
        for seg in Segmento.objects.all():
            self.stdout.write(f"  ID {seg.id}: {seg.nombre} (Tipo Canal: {seg.tipo_canal_id})")
        
        # Ver Tipificaciones actuales
        self.stdout.write("\n🏷️  TIPIFICACIONES ACTUALES:")
        for tip in Tipificacion.objects.all():
            self.stdout.write(f"  ID {tip.id}: {tip.nombre}")
        
        # Ver Categorías actuales
        self.stdout.write("\n📋 CATEGORÍAS ACTUALES:")
        for cat in Categoria.objects.all().order_by('nivel', 'id'):
            padre = f" (Padre: {cat.categoria_padre_id})" if cat.categoria_padre_id else ""
            self.stdout.write(f"  ID {cat.id}: {cat.nombre} - Nivel {cat.nivel}{padre}")
        
        # Ver Evaluaciones existentes
        eval_count = Evaluacion.objects.count()
        self.stdout.write(f"\n📝 EVALUACIONES EXISTENTES: {eval_count}")