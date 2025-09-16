from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ===================== MAESTROS =====================

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
    correo = models.EmailField("Correo electrónico", max_length=254, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    direccion_residencia = models.CharField("Dirección de residencia", max_length=255, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, null=True, blank=True)
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


# ===================== SEGMENTOS 1 → 6 =====================

class Segmento(models.Model):
    nombre = models.CharField(max_length=200)
    tipo_canal = models.ForeignKey(TipoCanal, on_delete=models.CASCADE, null=True, blank=True)
    tiene_segmento_ii = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Segmento"
        verbose_name_plural = "Segmentos"
        ordering = ['tipo_canal', 'nombre']

    def __str__(self):
        tc = self.tipo_canal.nombre if self.tipo_canal else "Sin canal"
        return f"{tc} - {self.nombre}"


class SegmentoII(models.Model):
    nombre = models.CharField(max_length=200)
    segmento = models.ForeignKey(Segmento, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Segmento II"
        verbose_name_plural = "Segmentos II"
        ordering = ['segmento', 'nombre']

    def __str__(self):
        return f"{self.segmento.nombre} - {self.nombre}"


class SegmentoIII(models.Model):
    nombre = models.CharField(max_length=200)
    segmento_ii = models.ForeignKey(SegmentoII, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Segmento III"
        verbose_name_plural = "Segmentos III"
        ordering = ['segmento_ii', 'nombre']

    def __str__(self):
        return f"{self.segmento_ii.segmento.nombre} - {self.segmento_ii.nombre} - {self.nombre}"


class SegmentoIV(models.Model):
    nombre = models.CharField(max_length=200)
    segmento_iii = models.ForeignKey(SegmentoIII, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Segmento IV"
        verbose_name_plural = "Segmentos IV"
        ordering = ['segmento_iii', 'nombre']

    def __str__(self):
        s2 = self.segmento_iii.segmento_ii
        s1 = s2.segmento
        return f"{s1.nombre} - {s2.nombre} - {self.segmento_iii.nombre} - {self.nombre}"


class SegmentoV(models.Model):
    nombre = models.CharField(max_length=200)
    segmento_iv = models.ForeignKey(SegmentoIV, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Segmento V"
        verbose_name_plural = "Segmentos V"
        ordering = ['segmento_iv', 'nombre']

    def __str__(self):
        s3 = self.segmento_iv.segmento_iii
        s2 = s3.segmento_ii
        s1 = s2.segmento
        return f"{s1.nombre} - {s2.nombre} - {s3.nombre} - {self.segmento_iv.nombre} - {self.nombre}"


class SegmentoVI(models.Model):
    nombre = models.CharField(max_length=200)
    segmento_v = models.ForeignKey(SegmentoV, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Segmento VI"
        verbose_name_plural = "Segmentos VI"
        ordering = ['segmento_v', 'nombre']

    def __str__(self):
        s4 = self.segmento_v.segmento_iv
        s3 = s4.segmento_iii
        s2 = s3.segmento_ii
        s1 = s2.segmento
        return f"{s1.nombre} - {s2.nombre} - {s3.nombre} - {s4.nombre} - {self.segmento_v.nombre} - {self.nombre}"


# ===================== TIPIFICACIÓN / CATEGORÍAS (1 → 6) =====================

class Tipificacion(models.Model):
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Tipificación"
        verbose_name_plural = "Tipificaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """
    Árbol de categorías hasta nivel 6:
    nivel=1 (raíz), 2, 3, 4, 5, 6 (terminal)
    """
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
        return f"{self.nombre} - {self.categoria_padre.nombre if self.categoria_padre else 'Sin padre'}"


# ===================== EVALUACIÓN =====================

class Evaluacion(models.Model):
    conversacion_id = models.CharField(max_length=250)
    observacion = models.TextField()
    ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE)

    # Tipificación y categoría final (1→6)
    tipificacion = models.ForeignKey(Tipificacion, on_delete=models.CASCADE, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)

    # Canal / Segmentos (hasta VI)
    tipo_canal = models.ForeignKey(TipoCanal, on_delete=models.CASCADE, null=True, blank=True)
    segmento = models.ForeignKey(Segmento, on_delete=models.CASCADE, null=True, blank=True)
    segmento_ii = models.ForeignKey(SegmentoII, on_delete=models.CASCADE, null=True, blank=True)
    segmento_iii = models.ForeignKey(SegmentoIII, on_delete=models.CASCADE, null=True, blank=True)
    segmento_iv = models.ForeignKey(SegmentoIV, on_delete=models.CASCADE, null=True, blank=True)
    segmento_v  = models.ForeignKey(SegmentoV,  on_delete=models.CASCADE, null=True, blank=True)
    segmento_vi = models.ForeignKey(SegmentoVI, on_delete=models.CASCADE, null=True, blank=True)

    # Metadatos
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now=True)

    # Contacto si es anónimo
    es_anonimo = models.BooleanField(default=False, db_index=True)
    contacto_correo = models.EmailField("Correo de contacto", max_length=254, blank=True, null=True, db_index=True)
    contacto_telefono = models.CharField("Teléfono de contacto", max_length=20, blank=True, null=True, db_index=True)
    contacto_telefono_inconcer = models.CharField("Teléfono Inconcer (contacto)", max_length=20, blank=True, null=True, db_index=True)

    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.ciudadano.nombre} - {self.fecha}"


# ===================== ENCUESTA =====================

class Encuesta(models.Model):
    """
    Encuesta asociada 1:N a Evaluacion. Token único y expiración.
    Los campos de métricas (abajo) se mantienen por compatibilidad,
    pero la recomendación es usar RespuestaEncuesta para almacenar respuestas.
    """
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='encuestas')

    # --- (LEGADO / Compatibilidad) ---
    dominioPersonaAtendio = models.IntegerField(null=True, blank=True)
    satisfaccionServicioRecibido = models.IntegerField(null=True, blank=True)
    tiempoEsperaServicio = models.IntegerField(null=True, blank=True)
    recomendacionCanalAtencion = models.IntegerField(null=True, blank=True)
    solucionSolicitud = models.BooleanField(null=True, blank=True)
    # ----------------------------------

    idInteraccion = models.CharField(max_length=150)
    seleccionarCanal = models.CharField(max_length=150, null=True, blank=True)
    nombreAgente = models.CharField(max_length=150)

    token = models.CharField(max_length=50, unique=True, db_index=True)
    fechaExpiracionLink = models.DateTimeField(db_index=True)
    fecha_creacion = models.DateTimeField(null=True, db_index=True)

    class Meta:
        verbose_name = "Encuesta"
        verbose_name_plural = "Encuestas"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Encuesta {self.token} (Eval {self.evaluacion_id})"

    @property
    def expirada(self):
        return timezone.now() > self.fechaExpiracionLink


# ===================== PREGUNTAS DINÁMICAS DE ENCUESTA =====================

class PreguntaEncuesta(models.Model):
    texto = models.CharField(max_length=255)
    tipo = models.CharField(
        max_length=20,
        choices=[("escala", "Escala 1-5"), ("si_no", "Sí/No")],
        default="escala"
    )
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Pregunta de Encuesta"
        verbose_name_plural = "Preguntas de Encuesta"
        ordering = ["orden"]

    def __str__(self):
        return f"{self.orden}. {self.texto}"


class RespuestaEncuesta(models.Model):
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name="respuestas")
    pregunta = models.ForeignKey(PreguntaEncuesta, on_delete=models.CASCADE)
    valor = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Respuesta de Encuesta"
        verbose_name_plural = "Respuestas de Encuesta"
        constraints = [
            models.UniqueConstraint(
                fields=["encuesta", "pregunta"],
                name="uniq_encuesta_pregunta"
            )
        ]

    def __str__(self):
        return f"{self.pregunta.texto} → {self.valor}"


# ===================== LOG ERRORES =====================

class RegistroError(models.Model):
    metodo = models.CharField(max_length=100)
    excepcion = models.TextField()
    fecha = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
