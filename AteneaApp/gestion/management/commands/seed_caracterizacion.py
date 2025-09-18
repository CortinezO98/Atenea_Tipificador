from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import *
from gestion.management.data.sexos import sexos
from gestion.management.data.generos import generos
from gestion.management.data.orientaciones import orientaciones
from gestion.management.data.tieneDiscapacidad import tieneDiscapacidad
from gestion.management.data.discapacidades import discapacidades
from gestion.management.data.rangosEdad import rangosEdad
from gestion.management.data.nivelesEducativos import nivelesEducativos
from gestion.management.data.gruposEtnicos import gruposEtnicos
from gestion.management.data.gruposPoblacionales import gruposPoblacionales
from gestion.management.data.estratos import estratos
from gestion.management.data.localidades import localidades
from gestion.management.data.calidades import calidades

def upsert(model, data_list):
    for d in data_list:
        obj, created = model.objects.get_or_create(id=d["id"], defaults={"nombre": d["nombre"]})
        if not created and obj.nombre != d["nombre"]:
            obj.nombre = d["nombre"]
            obj.save(update_fields=["nombre"])

class Command(BaseCommand):
    help = "Carga/actualiza catálogos de caracterización por IDs fijos."

    @transaction.atomic
    def handle(self, *args, **opts):
        upsert(Sexo, sexos)
        upsert(Genero, generos)
        upsert(OrientacionSexual, orientaciones)
        upsert(TieneDiscapacidad, tieneDiscapacidad)
        upsert(Discapacidad, discapacidades)
        upsert(RangoEdad, rangosEdad)
        upsert(NivelEducativo, nivelesEducativos)
        upsert(GrupoEtnico, gruposEtnicos)
        upsert(GrupoPoblacional, gruposPoblacionales)
        upsert(Estrato, estratos)
        upsert(Localidad, localidades)
        upsert(CalidadComunicacion, calidades)
        self.stdout.write(self.style.SUCCESS("✅ Catálogos de caracterización cargados"))