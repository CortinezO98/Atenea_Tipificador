from django.core.management.base import BaseCommand
from gestion.models import Tipificacion, Categoria
from django.db import transaction

class Command(BaseCommand):
    help = 'Verifica y corrige tipificaciones para producción'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Aplica las correcciones automáticamente',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VERIFICACIÓN DE TIPIFICACIONES ==='))
        
        problemas_encontrados = []
        
        # 1. Verificar PRESENCIA INMEDIATA DE POLICIA
        self.stdout.write('\n1. Verificando PRESENCIA INMEDIATA DE POLICIA...')
        tip_presencia = Tipificacion.objects.filter(nombre="PRESENCIA INMEDIATA DE LA POLICIA").first()
        
        if tip_presencia:
            categorias_principales = Categoria.objects.filter(
                tipificacion=tip_presencia,
                nombre="PRESENCIA INMEDIATA DE POLICIA"
            )
            
            if not categorias_principales.exists():
                problema = "Falta categoría principal para PRESENCIA INMEDIATA DE POLICIA"
                problemas_encontrados.append(problema)
                self.stdout.write(f"   ❌ {problema}")
                
                if options['fix']:
                    Categoria.objects.create(
                        nombre="PRESENCIA INMEDIATA DE POLICIA",
                        nivel=1,
                        tipificacion=tip_presencia,
                        categoria_padre=None
                    )
                    self.stdout.write(f"   ✅ Corregido: Creada categoría principal")
            else:
                self.stdout.write("   ✅ Categoría principal OK")
        else:
            problema = "Tipificación PRESENCIA INMEDIATA DE POLICIA no encontrada"
            problemas_encontrados.append(problema)
            self.stdout.write(f"   ❌ {problema}")

        # 2. Verificar NO EFECTIVO
        self.stdout.write('\n2. Verificando NO EFECTIVO...')
        tip_no_efectivo = Tipificacion.objects.filter(nombre="NO EFECTIVO").first()
        
        if tip_no_efectivo:
            categorias_no_efectivo = Categoria.objects.filter(tipificacion=tip_no_efectivo)
            
            if not categorias_no_efectivo.exists():
                problema = "Falta categoría para NO EFECTIVO"
                problemas_encontrados.append(problema)
                self.stdout.write(f"   ❌ {problema}")
                
                if options['fix']:
                    Categoria.objects.create(
                        nombre="NO EFECTIVO",
                        nivel=1,
                        tipificacion=tip_no_efectivo,
                        categoria_padre=None
                    )
                    self.stdout.write(f"   ✅ Corregido: Creada categoría NO EFECTIVO")
            else:
                self.stdout.write("   ✅ Categorías NO EFECTIVO OK")
        else:
            problema = "Tipificación NO EFECTIVO no encontrada"
            problemas_encontrados.append(problema)
            self.stdout.write(f"   ❌ {problema}")

        # 3. Verificar tipificaciones sin categorías
        self.stdout.write('\n3. Verificando tipificaciones sin categorías...')
        tipificaciones_sin_categorias = []
        
        for tip in Tipificacion.objects.all():
            if not Categoria.objects.filter(tipificacion=tip).exists():
                tipificaciones_sin_categorias.append(tip.nombre)
        
        if tipificaciones_sin_categorias:
            self.stdout.write(f"   ⚠️  {len(tipificaciones_sin_categorias)} tipificaciones sin categorías:")
            for nombre in tipificaciones_sin_categorias:
                self.stdout.write(f"      - {nombre}")
        else:
            self.stdout.write("   ✅ Todas las tipificaciones tienen categorías")

        # Resumen
        self.stdout.write(f'\n=== RESUMEN ===')
        if problemas_encontrados:
            self.stdout.write(f'❌ {len(problemas_encontrados)} problemas encontrados')
            if not options['fix']:
                self.stdout.write('💡 Ejecuta con --fix para corregir automáticamente')
        else:
            self.stdout.write('✅ Todo está correcto')