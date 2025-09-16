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
    list_display = ('nombre','tipo_identificacion','numero_identificacion','correo','telefono','pais','ciudad',)
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
    list_display = ('ciudadano', 'tipo_canal', 'segmento', 'tipificacion', 'categoria', 'user', 'fecha', 'se_comunica_uri', 'consulta_juridica')
    list_filter = ('fecha', 'user', 'tipo_canal', 'segmento', 'tipificacion', 'se_comunica_uri', 'consulta_juridica')
    search_fields = ('ciudadano__nombre', 'observacion', 'ciudad_municipio_uri')

@admin.register(Abogado)
class AbogadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'especialidad', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'especialidad', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'especialidad')
    list_editable = ('activo',)
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'email', 'telefono')
        }),
        ('Información Profesional', {
            'fields': ('especialidad', 'activo')
        }),
    )

@admin.register(Delito)
class DelitoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('activo',)
    ordering = ('codigo', 'nombre')
    
    fieldsets = (
        ('Información del Delito', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

@admin.register(CasoAbogado)
class CasoAbogadoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ciudadano_nombre', 'abogado', 'estado', 'prioridad', 
        'delito_codigo', 'interaccion_directa_display', 'habeas_corpus_display', 'tutela_display',
        'fecha_asignacion', 'fecha_tipificacion_agente', 'tiempo_respuesta_horas'
    )
    list_filter = (
        'estado', 'prioridad', 'fecha_asignacion', 'fecha_tipificacion_agente', 'abogado', 
        'evaluacion__categoria__tipificacion', 'delito',
        'interaccion_directa_usuario', 'habeas_corpus', 'tutela'
    )
    search_fields = (
        'evaluacion__ciudadano__nombre',
        'evaluacion__ciudadano__numero_identificacion',
        'abogado__nombre',
        'evaluacion__categoria__tipificacion__nombre',
        'delito__codigo', 'delito__nombre'
    )
    list_editable = ('estado', 'prioridad')
    readonly_fields = ('fecha_asignacion', 'fecha_tipificacion_agente', 'tiempo_respuesta_horas')
    
    fieldsets = (
        ('Información del Caso', {
            'fields': ('evaluacion', 'abogado', 'fecha_asignacion')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad', 'fecha_revision', 'fecha_completado', 'fecha_tipificacion_agente', 'tiempo_respuesta_horas')
        }),
        ('Análisis Jurídico', {
            'fields': ('delito', 'interaccion_directa_usuario', 'habeas_corpus', 'tutela'),
            'description': 'Campos específicos del análisis jurídico realizado por el abogado'
        }),
        ('Observaciones del Abogado', {
            'fields': ('observaciones_abogado',),
            'classes': ('collapse',)
        }),
    )
    
    def ciudadano_nombre(self, obj):
        return obj.evaluacion.ciudadano.nombre
    ciudadano_nombre.short_description = 'Ciudadano'
    ciudadano_nombre.admin_order_field = 'evaluacion__ciudadano__nombre'
    
    def delito_codigo(self, obj):
        return f"{obj.delito.codigo} - {obj.delito.nombre}" if obj.delito else 'Sin delito asignado'
    delito_codigo.short_description = 'Delito'
    delito_codigo.admin_order_field = 'delito__codigo'
    
    def interaccion_directa_display(self, obj):
        if obj.interaccion_directa_usuario is True:
            return "SÍ"
        elif obj.interaccion_directa_usuario is False:
            return "NO"
        return "N/A"
    interaccion_directa_display.short_description = 'Interacción Directa'
    
    def habeas_corpus_display(self, obj):
        if obj.habeas_corpus is True:
            return "SÍ"
        elif obj.habeas_corpus is False:
            return "NO"
        return "N/A"
    habeas_corpus_display.short_description = 'Habeas Corpus'
    
    def tutela_display(self, obj):
        if obj.tutela is True:
            return "SÍ"
        elif obj.tutela is False:
            return "NO"
        return "N/A"
    tutela_display.short_description = 'Tutela'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'evaluacion__ciudadano',
            'abogado',
            'evaluacion__categoria__tipificacion',
            'delito'
        )    

@admin.register(RegistroError)
class RegistroErrorAdmin(admin.ModelAdmin):
    list_display = ('metodo', 'excepcion', 'usuario', 'fecha')
    list_filter = ('metodo',)
    search_fields = ('metodo',)