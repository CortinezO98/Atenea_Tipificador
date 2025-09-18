# gestion/management/commands/seed_gestion.py
from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import (
    TipoIdentificacion, TipoCanal,
    Segmento, SegmentoII, SegmentoIII,
    Tipificacion, Categoria,
)

# Importaciones obligatorias (estos archivos sí existen en tu proyecto)
from gestion.management.data.tiposIdentificacion import tiposIdentificacion
from gestion.management.data.tiposCanal import tiposCanal

# Importaciones opcionales (si no están, no rompen el comando)
try:
    from gestion.management.data.segmentos import segmentos
except Exception:
    segmentos = []

try:
    from gestion.management.data.segmentosII import segmentosII
except Exception:
    segmentosII = []

try:
    from gestion.management.data.segmentosIII import segmentosIII
except Exception:
    segmentosIII = []

try:
    from gestion.management.data.tipificaciones import tipificaciones
except Exception:
    tipificaciones = []

try:
    from gestion.management.data.categorias import categorias
except Exception:
    categorias = []


class Command(BaseCommand):
    help = 'Carga datos de la nueva estructura de tipificación (tolerante a faltantes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only',
            choices=['all', 'tipos_id', 'tipo_canal', 'segmentos', 'segmentos2', 'segmentos3', 'tipificaciones', 'categorias'],
            default='all',
            help="Sembrar solo una parte. Ej: --only tipo_canal"
        )

    def handle(self, *args, **options):
        only = options['only']
        try:
            with transaction.atomic():
                if only in ('all', 'tipos_id'):
                    self.CrearTiposIdentificacion()
                if only in ('all', 'tipo_canal'):
                    self.CrearTiposCanal()
                if only in ('all', 'segmentos'):
                    self.CrearSegmentos()
                if only in ('all', 'segmentos2'):
                    self.CrearSegmentosII()
                if only in ('all', 'segmentos3'):
                    self.CrearSegmentosIII()
                if only in ('all', 'tipificaciones'):
                    self.CrearTipificaciones()
                if only in ('all', 'categorias'):
                    self.CrearCategorias()

                self.stdout.write(self.style.SUCCESS('✅ Seed completado.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error, se hizo rollback: {e}'))

    # ---------- CARGAS ----------

    def CrearTiposIdentificacion(self):
        creados = 0
        for d in tiposIdentificacion:
            obj, created = TipoIdentificacion.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre']},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearTiposIdentificacion OK (nuevos={creados})'))

    def CrearTiposCanal(self):
        creados = 0
        for d in tiposCanal:
            obj, created = TipoCanal.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre']},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearTiposCanal OK (nuevos={creados})'))

    def CrearSegmentos(self):
        if not segmentos:
            self.stdout.write(self.style.WARNING('CrearSegmentos: no hay data (segmentos.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in segmentos:
            obj, created = Segmento.objects.update_or_create(
                id=d['id'],
                defaults={
                    'nombre': d['nombre'],
                    'tipo_canal_id': d.get('tipo_canal_id'),
                    'tiene_segmento_ii': bool(d.get('tiene_segmento_ii', False)),
                },
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearSegmentos OK (nuevos={creados})'))

    def CrearSegmentosII(self):
        if not segmentosII:
            self.stdout.write(self.style.WARNING('CrearSegmentosII: no hay data (segmentosII.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in segmentosII:
            obj, created = SegmentoII.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre'], 'segmento_id': d.get('segmento_id')},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearSegmentosII OK (nuevos={creados})'))

    def CrearSegmentosIII(self):
        if not segmentosIII:
            self.stdout.write(self.style.WARNING('CrearSegmentosIII: no hay data (segmentosIII.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in segmentosIII:
            obj, created = SegmentoIII.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre'], 'segmento_ii_id': d.get('segmento_ii_id')},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearSegmentosIII OK (nuevos={creados})'))

    def CrearTipificaciones(self):
        if not tipificaciones:
            self.stdout.write(self.style.WARNING('CrearTipificaciones: no hay data (tipificaciones.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in tipificaciones:
            obj, created = Tipificacion.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre']},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearTipificaciones OK (nuevos={creados})'))

    def CrearCategorias(self):
        if not categorias:
            self.stdout.write(self.style.WARNING('CrearCategorias: no hay data (categorias.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in categorias:
            defaults = {
                'nombre': d['nombre'],
                'nivel': int(d['nivel']),
                'tipificacion_id': int(d['tipificacion_id']) if d.get('tipificacion_id') else None,
                'categoria_padre_id': int(d['categoria_padre_id']) if d.get('categoria_padre_id') else None,
            }
            obj, created = Categoria.objects.update_or_create(
                id=d['id'],
                defaults=defaults,
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearCategorias OK (nuevos={creados})'))
# gestion/management/commands/seed_gestion.py
from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import (
    TipoIdentificacion, TipoCanal,
    Segmento, SegmentoII, SegmentoIII,
    Tipificacion, Categoria,
)

# Importaciones obligatorias (estos archivos sí existen en tu proyecto)
from gestion.management.data.tiposIdentificacion import tiposIdentificacion
from gestion.management.data.tiposCanal import tiposCanal

# Importaciones opcionales (si no están, no rompen el comando)
try:
    from gestion.management.data.segmentos import segmentos
except Exception:
    segmentos = []

try:
    from gestion.management.data.segmentosII import segmentosII
except Exception:
    segmentosII = []

try:
    from gestion.management.data.segmentosIII import segmentosIII
except Exception:
    segmentosIII = []

try:
    from gestion.management.data.tipificaciones import tipificaciones
except Exception:
    tipificaciones = []

try:
    from gestion.management.data.categorias import categorias
except Exception:
    categorias = []


class Command(BaseCommand):
    help = 'Carga datos de la nueva estructura de tipificación (tolerante a faltantes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only',
            choices=['all', 'tipos_id', 'tipo_canal', 'segmentos', 'segmentos2', 'segmentos3', 'tipificaciones', 'categorias'],
            default='all',
            help="Sembrar solo una parte. Ej: --only tipo_canal"
        )

    def handle(self, *args, **options):
        only = options['only']
        try:
            with transaction.atomic():
                if only in ('all', 'tipos_id'):
                    self.CrearTiposIdentificacion()
                if only in ('all', 'tipo_canal'):
                    self.CrearTiposCanal()
                if only in ('all', 'segmentos'):
                    self.CrearSegmentos()
                if only in ('all', 'segmentos2'):
                    self.CrearSegmentosII()
                if only in ('all', 'segmentos3'):
                    self.CrearSegmentosIII()
                if only in ('all', 'tipificaciones'):
                    self.CrearTipificaciones()
                if only in ('all', 'categorias'):
                    self.CrearCategorias()

                self.stdout.write(self.style.SUCCESS('✅ Seed completado.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error, se hizo rollback: {e}'))

    # ---------- CARGAS ----------

    def CrearTiposIdentificacion(self):
        creados = 0
        for d in tiposIdentificacion:
            obj, created = TipoIdentificacion.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre']},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearTiposIdentificacion OK (nuevos={creados})'))

    def CrearTiposCanal(self):
        creados = 0
        for d in tiposCanal:
            obj, created = TipoCanal.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre']},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearTiposCanal OK (nuevos={creados})'))

    def CrearSegmentos(self):
        if not segmentos:
            self.stdout.write(self.style.WARNING('CrearSegmentos: no hay data (segmentos.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in segmentos:
            obj, created = Segmento.objects.update_or_create(
                id=d['id'],
                defaults={
                    'nombre': d['nombre'],
                    'tipo_canal_id': d.get('tipo_canal_id'),
                    'tiene_segmento_ii': bool(d.get('tiene_segmento_ii', False)),
                },
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearSegmentos OK (nuevos={creados})'))

    def CrearSegmentosII(self):
        if not segmentosII:
            self.stdout.write(self.style.WARNING('CrearSegmentosII: no hay data (segmentosII.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in segmentosII:
            obj, created = SegmentoII.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre'], 'segmento_id': d.get('segmento_id')},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearSegmentosII OK (nuevos={creados})'))

    def CrearSegmentosIII(self):
        if not segmentosIII:
            self.stdout.write(self.style.WARNING('CrearSegmentosIII: no hay data (segmentosIII.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in segmentosIII:
            obj, created = SegmentoIII.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre'], 'segmento_ii_id': d.get('segmento_ii_id')},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearSegmentosIII OK (nuevos={creados})'))

    def CrearTipificaciones(self):
        if not tipificaciones:
            self.stdout.write(self.style.WARNING('CrearTipificaciones: no hay data (tipificaciones.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in tipificaciones:
            obj, created = Tipificacion.objects.update_or_create(
                id=d['id'],
                defaults={'nombre': d['nombre']},
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearTipificaciones OK (nuevos={creados})'))

    def CrearCategorias(self):
        if not categorias:
            self.stdout.write(self.style.WARNING('CrearCategorias: no hay data (categorias.py ausente o vacío). Saltando.'))
            return
        creados = 0
        for d in categorias:
            defaults = {
                'nombre': d['nombre'],
                'nivel': int(d['nivel']),
                'tipificacion_id': int(d['tipificacion_id']) if d.get('tipificacion_id') else None,
                'categoria_padre_id': int(d['categoria_padre_id']) if d.get('categoria_padre_id') else None,
            }
            obj, created = Categoria.objects.update_or_create(
                id=d['id'],
                defaults=defaults,
            )
            creados += int(created)
        self.stdout.write(self.style.SUCCESS(f'CrearCategorias OK (nuevos={creados})'))
