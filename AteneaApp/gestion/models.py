from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TipoIdentificacion(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tipo documento"
        verbose_name_plural = "Tipos de documentos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre}"


class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    

class Ciudadano(models.Model):
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.CASCADE)
    numero_identificacion = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    correo  = models.EmailField("Correo electrónico", max_length=254, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    direccion_residencia = models.CharField("Dirección de residencia", max_length=255, blank=True)
    pais  = models.ForeignKey(Pais, on_delete=models.PROTECT, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Ciudadano"
        verbose_name_plural = "Ciudadanos"
        indexes = [models.Index(fields=['numero_identificacion'])]

    def __str__(self):
        return f"{self.nombre} ({self.tipo_identificacion} {self.numero_identificacion})"
    

class TipoCanal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tipo de Canal"
        verbose_name_plural = "Tipos de Canal"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Segmento(models.Model):
    nombre = models.CharField(max_length=200)
    tipo_canal = models.ForeignKey(TipoCanal, on_delete=models.CASCADE, null=True, blank=True)  # Nueva relación
    tiene_segmento_ii = models.BooleanField(default=False)  # Indica si necesita Segmento II
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Segmento"
        verbose_name_plural = "Segmentos"
        ordering = ['tipo_canal', 'nombre']

    def __str__(self):
        return f"{self.tipo_canal.nombre} - {self.nombre}"
    

class SegmentoII(models.Model):  # Nuevo modelo
    nombre = models.CharField(max_length=200)
    segmento = models.ForeignKey(Segmento, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Segmento II"
        verbose_name_plural = "Segmentos II"
        ordering = ['segmento', 'nombre']

    def __str__(self):
        return f"{self.segmento.nombre} - {self.nombre}"

class SegmentoIII(models.Model):  # NUEVO MODELO AGREGADO
    nombre = models.CharField(max_length=200)
    segmento_ii = models.ForeignKey(SegmentoII, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Segmento III"
        verbose_name_plural = "Segmentos III"
        ordering = ['segmento_ii', 'nombre']

    def __str__(self):
        return f"{self.segmento_ii.segmento.nombre} - {self.segmento_ii.nombre} - {self.nombre}"

class Tipificacion(models.Model):
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Tipificación"
        verbose_name_plural = "Tipificaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=200)
    nivel = models.IntegerField(default=1, db_index=True)
    tipificacion = models.ForeignKey(Tipificacion, null=True, blank=True, on_delete=models.CASCADE)
    categoria_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='categoriapadre')

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nombre']

    def __str__(self):
        if self.tipificacion:
            return f"{self.nombre} - {self.tipificacion.nombre}"
        else:
            return f"{self.nombre} - {self.categoria_padre.nombre if self.categoria_padre else 'Sin padre'}"


# Actualizar el modelo Evaluacion en gestion/models.py

class Evaluacion(models.Model):
    conversacion_id = models.CharField(max_length=250)
    observacion = models.TextField()
    ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE)
    
    # Campos antiguos (mantener temporalmente)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now=True)
    
    # Nuevos campos (nullable para migración)
    tipo_canal = models.ForeignKey(TipoCanal, on_delete=models.CASCADE, null=True, blank=True)
    segmento = models.ForeignKey(Segmento, on_delete=models.CASCADE, null=True, blank=True)
    segmento_ii = models.ForeignKey(SegmentoII, on_delete=models.CASCADE, null=True, blank=True)
    segmento_iii = models.ForeignKey(SegmentoIII, on_delete=models.CASCADE, null=True, blank=True)  # NUEVO CAMPO
    tipificacion = models.ForeignKey(Tipificacion, on_delete=models.CASCADE, null=True, blank=True)
    
    # Campo especial para "OTROS DELITOS"
    cual_otro_delito = models.CharField(max_length=500, blank=True, null=True, 
                                      verbose_name="¿Cuál otro delito?",
                                      help_text="Solo se llena cuando se selecciona 'OTROS DELITOS'")
    
    # Campos luego de tipificación
    se_comunica_uri = models.BooleanField(null=True, blank=True, verbose_name="Se comunica de una URI")
    ciudad_municipio_uri = models.CharField(max_length=200, blank=True, verbose_name="Ciudad/Municipio URI")
    
    consulta_juridica = models.BooleanField(null=True, blank=True, verbose_name="Consulta jurídica")
    abogado = models.ForeignKey('Abogado', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Abogado asignado")

    es_anonimo = models.BooleanField(default=False, db_index=True)
    contacto_correo   = models.EmailField("Correo de contacto", max_length=254, blank=True, null=True, db_index=True)
    contacto_telefono = models.CharField("Teléfono de contacto", max_length=20,  blank=True, null=True, db_index=True)
    contacto_telefono_inconcer = models.CharField("Teléfono Inconcer (contacto)", max_length=20, blank=True, null=True, db_index=True)



    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.ciudadano.nombre} - {self.fecha}"
    
# NUEVO MODELO PARA ABOGADOS
class Abogado(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    especialidad = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Abogado"
        verbose_name_plural = "Abogados"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre}"

class Delito(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    codigo = models.CharField(max_length=50, blank=True, verbose_name="Código del delito")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del delito")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Delito"
        verbose_name_plural = "Delitos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}" if self.codigo else self.nombre


# Actualizar el modelo CasoAbogado agregando los nuevos campos
class CasoAbogado(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_REVISION', 'En Revisión'),
        ('COMPLETADO', 'Completado'),
        ('CERRADO', 'Cerrado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
    ]

    evaluacion = models.OneToOneField(Evaluacion, on_delete=models.CASCADE, related_name='caso_abogado')
    abogado = models.ForeignKey(Abogado, on_delete=models.CASCADE, related_name='casos_asignados')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    # NUEVO CAMPO AGREGADO
    fecha_tipificacion_agente = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de tipificación del abogado")
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')
    
    # Campos para que el abogado complete
    observaciones_abogado = models.TextField(blank=True, verbose_name="Observaciones del abogado")
    
    # Campos jurídicos activos
    delito = models.ForeignKey(Delito, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Delito identificado")
    interaccion_directa_usuario = models.BooleanField(null=True, blank=True, verbose_name="Interacción directa con el usuario")
    habeas_corpus = models.BooleanField(null=True, blank=True, verbose_name="Habeas Corpus")
    tutela = models.BooleanField(null=True, blank=True, verbose_name="Tutela")
    
    # Campo de seguimiento
    tiempo_respuesta_horas = models.IntegerField(null=True, blank=True, verbose_name="Tiempo de respuesta (horas)")
    
    class Meta:
        verbose_name = "Caso de Abogado"
        verbose_name_plural = "Casos de Abogados"
        ordering = ['-fecha_asignacion']

    def __str__(self):
        return f"Caso #{self.id} - {self.evaluacion.ciudadano.nombre} - {self.abogado.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular tiempo de respuesta automáticamente
        if self.estado == 'EN_REVISION' and not self.fecha_revision:
            self.fecha_revision = timezone.now()
        elif self.estado == 'COMPLETADO' and not self.fecha_completado:
            self.fecha_completado = timezone.now()
            
        # NUEVA LÓGICA: Registrar fecha de tipificación del abogado
        # Se registra la primera vez que el abogado hace algún cambio
        if not self.fecha_tipificacion_agente:
            # Verificar si es una actualización (no creación) y tiene datos del abogado
            if self.pk and (self.observaciones_abogado or self.delito or 
                           self.interaccion_directa_usuario is not None or 
                           self.habeas_corpus is not None or 
                           self.tutela is not None):
                self.fecha_tipificacion_agente = timezone.now()
        
        super().save(*args, **kwargs)       


class RegistroError(models.Model):
    metodo = models.CharField(max_length=100)
    excepcion = models.TextField()
    fecha = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)