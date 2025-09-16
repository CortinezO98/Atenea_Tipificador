from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import *
from gestion.management.data.tiposIdentificacion import tiposIdentificacion
from gestion.management.data.tiposCanal import tiposCanal
from gestion.management.data.segmentos import segmentos
from gestion.management.data.segmentosII import segmentosII
from gestion.management.data.segmentosIII import segmentosIII
from gestion.management.data.tipificaciones import tipificaciones
from gestion.management.data.categorias import categorias

class Command(BaseCommand):
    help = 'Carga datos de la nueva estructura de tipificación'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                CrearTiposIdentificacion()
                CrearTiposCanal()
                CrearSegmentos()
                CrearSegmentosII()
                CrearSegmentosIII()  # Nueva función agregada
                CrearTipificaciones()
                CrearCategorias()
                self.stdout.write(self.style.SUCCESS('Nueva estructura de datos creada correctamente.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error, se hizo rollback: {e}'))

def CrearTiposIdentificacion():
    for tipoIdentificacionData in tiposIdentificacion:
        tipoIdentificacion = TipoIdentificacion.objects.filter(id=tipoIdentificacionData['id']).first()
        if not tipoIdentificacion:
            TipoIdentificacion.objects.create(
                id=tipoIdentificacionData['id'],
                nombre=tipoIdentificacionData['nombre']
            )
    print('CrearTiposIdentificacion se ejecutó correctamente.')


def CrearTiposCanal():  # Nueva función
    for tipoCanalData in tiposCanal:
        tipoCanal = TipoCanal.objects.filter(id=tipoCanalData['id']).first()
        if not tipoCanal:
            TipoCanal.objects.create(
                id=tipoCanalData['id'],
                nombre=tipoCanalData['nombre']
            )
    print('CrearTiposCanal se ejecutó correctamente.')    


def CrearSegmentos():
    for segmentoData in segmentos:
        segmento = Segmento.objects.filter(id=segmentoData['id']).first()
        if not segmento:
            Segmento.objects.create(
                id=segmentoData['id'],
                nombre=segmentoData['nombre'],
                tipo_canal_id=segmentoData['tipo_canal_id'],
                tiene_segmento_ii=segmentoData['tiene_segmento_ii']
            )
    print('CrearSegmentos se ejecutó correctamente.')

def CrearSegmentosII():
    for segmentoIIData in segmentosII:
        segmentoII = SegmentoII.objects.filter(id=segmentoIIData['id']).first()
        if not segmentoII:
            SegmentoII.objects.create(
                id=segmentoIIData['id'],
                nombre=segmentoIIData['nombre'],
                segmento_id=segmentoIIData['segmento_id']
            )
    print('CrearSegmentosII se ejecutó correctamente.')    

def CrearSegmentosIII():
    """Nueva función para cargar SegmentosIII"""
    for segmentoIIIData in segmentosIII:
        segmentoIII = SegmentoIII.objects.filter(id=segmentoIIIData['id']).first()
        if not segmentoIII:
            SegmentoIII.objects.create(
                id=segmentoIIIData['id'],
                nombre=segmentoIIIData['nombre'],
                segmento_ii_id=segmentoIIIData['segmento_ii_id']
            )
    print('CrearSegmentosIII se ejecutó correctamente.')

def CrearTipificaciones():
    for tipificacionData in tipificaciones:
        tipificacion = Tipificacion.objects.filter(id=tipificacionData['id']).first()
        if not tipificacion:
            Tipificacion.objects.create(
                id=tipificacionData['id'],
                nombre=tipificacionData['nombre'],
            )
    print('CrearTipificaciones se ejecutó correctamente.')

def CrearCategorias():
    for categoriaData in categorias:
        categoria = Categoria.objects.filter(id=categoriaData['id']).first()
        if not categoria:
            categoria = Categoria(
                id=categoriaData['id'],
                nombre=categoriaData['nombre'],
                nivel=int(categoriaData['nivel'])  
            )
            if categoriaData['tipificacion_id']:
                categoria.tipificacion_id=int(categoriaData['tipificacion_id'])

            if categoriaData['categoria_padre_id']:
                categoria.categoria_padre_id=int(categoriaData['categoria_padre_id'])
            
            categoria.save()
    print('CrearCategorias se ejecutó correctamente.')