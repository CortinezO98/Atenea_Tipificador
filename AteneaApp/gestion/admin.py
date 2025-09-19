# admin.py
from django.contrib import admin
from .models import *

# ======= Catálogos básicos =======

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

# ======= NUEVOS catálogos de caracterización =======

@admin.register(Sexo)
class SexoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(OrientacionSexual)
class OrientacionSexualAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(TieneDiscapacidad)
class TieneDiscapacidadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Discapacidad)
class DiscapacidadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(RangoEdad)
class RangoEdadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(NivelEducativo)
class NivelEducativoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(GrupoEtnico)
class GrupoEtnicoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(GrupoPoblacional)
class GrupoPoblacionalAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Estrato)
class EstratoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(CalidadComunicacion)
class CalidadComunicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# ======= Ciudadano =======

@admin.register(Ciudadano)
class CiudadanoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'tipo_identificacion', 'numero_identificacion',
        'correo', 'telefono', 'pais', 'ciudad',
        'sexo', 'genero', 'orientacion',
        'tiene_discapacidad', 'discapacidad',
        'rango_edad', 'nivel_educativo', 'grupo_etnico', 'grupo_poblacional',
        'estrato', 'localidad', 'calidad_comunicacion',
    )
    search_fields = ('nombre', 'numero_identificacion', 'correo', 'telefono', 'ciudad')
    list_filter = (
        'tipo_identificacion', 'pais',
        'sexo', 'genero', 'orientacion',
        'tiene_discapacidad', 'discapacidad',
        'rango_edad', 'nivel_educativo', 'grupo_etnico', 'grupo_poblacional',
        'estrato', 'localidad', 'calidad_comunicacion',
    )

# ======= Segmentos =======

@admin.register(Segmento)
class SegmentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_canal', 'tiene_segmento_ii', 'activo')
    list_filter = ('tipo_canal', 'tiene_segmento_ii', 'activo')
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

# ======= Tipificación / Categorías =======

@admin.register(Tipificacion)
class TipificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'tipificacion', 'categoria_padre')
    list_filter = ('nivel', 'tipificacion')
    search_fields = ('nombre',)
    list_select_related = ('tipificacion', 'categoria_padre')

# ======= Evaluación =======

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ('ciudadano', 'tipo_canal', 'segmento', 'tipificacion', 'categoria', 'user', 'fecha')
    list_filter = ('fecha', 'user', 'tipo_canal', 'segmento', 'tipificacion')
    search_fields = ('ciudadano__nombre', 'observacion')
    list_select_related = ('ciudadano', 'tipo_canal', 'segmento', 'tipificacion', 'categoria', 'user')

# ======= Encuestas (opcional pero recomendado) =======

@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ('evaluacion', 'agente', 'token', 'fechaExpiracionLink', 'respondida_en', 'is_cerrada', 'is_expirada')
    search_fields = ('token', 'evaluacion__conversacion_id', 'evaluacion__ciudadano__nombre')
    list_filter = ('agente', 'respondida_en',)
    list_select_related = ('evaluacion', 'agente')

    @admin.display(boolean=True, description='Cerrada')
    def is_cerrada(self, obj):
        return obj.cerrada

    @admin.display(boolean=True, description='Expirada')
    def is_expirada(self, obj):
        return obj.expirada

@admin.register(PreguntaEncuesta)
class PreguntaEncuestaAdmin(admin.ModelAdmin):
    list_display = ('orden', 'texto', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('texto',)
    ordering = ('orden',)

@admin.register(RespuestaEncuesta)
class RespuestaEncuestaAdmin(admin.ModelAdmin):
    list_display = ('encuesta', 'pregunta', 'valor')
    list_filter = ('pregunta__tipo',)
    search_fields = ('encuesta__token', 'pregunta__texto', 'valor')
    list_select_related = ('encuesta', 'pregunta')

# ======= Registro de errores =======

@admin.register(RegistroError)
class RegistroErrorAdmin(admin.ModelAdmin):
    list_display = ('metodo', 'excepcion', 'usuario', 'fecha')
    list_filter = ('metodo',)
    search_fields = ('metodo',)
