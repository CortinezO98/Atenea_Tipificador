from django.contrib import admin
from .models import *

@admin.register(TipoIdentificacion)
class TipoIdentificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(TipoCanal)
class TipoCanalAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Ciudadano)
class CiudadanoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_identificacion', 'numero_identificacion', 'correo', 'telefono', 'pais', 'ciudad')
    search_fields = ('nombre','numero_identificacion','correo','telefono',)
    list_filter = ('tipo_identificacion','pais',)

@admin.register(Segmento)
class SegmentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_canal', 'tiene_segmento_ii')
    list_filter = ('tipo_canal', 'tiene_segmento_ii')
    search_fields = ('nombre',)

@admin.register(SegmentoII)
class SegmentoIIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'segmento')
    list_filter = ('segmento',)
    search_fields = ('nombre',)

@admin.register(SegmentoIII)
class SegmentoIIIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'segmento_ii')
    list_filter = ('segmento_ii',)
    search_fields = ('nombre',)

@admin.register(SegmentoIV)
class SegmentoIVAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'segmento_iii')
    list_filter = ('segmento_iii',)
    search_fields = ('nombre',)

@admin.register(SegmentoV)
class SegmentoVAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'segmento_iv')
    list_filter = ('segmento_iv',)
    search_fields = ('nombre',)

@admin.register(SegmentoVI)
class SegmentoVIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'segmento_v')
    list_filter = ('segmento_v',)
    search_fields = ('nombre',)

@admin.register(Tipificacion)
class TipificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'tipificacion', 'categoria_padre')
    list_filter = ('nivel', 'tipificacion')
    search_fields = ('nombre',)

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ('ciudadano', 'tipo_canal', 'segmento', 'tipificacion', 'categoria', 'user', 'fecha')
    list_filter = ('fecha', 'user', 'tipo_canal', 'segmento', 'tipificacion')
    search_fields = ('ciudadano__nombre', 'observacion')

@admin.register(RegistroError)
class RegistroErrorAdmin(admin.ModelAdmin):
    list_display = ('metodo', 'excepcion', 'usuario', 'fecha')
    list_filter = ('metodo',)
    search_fields = ('metodo',)