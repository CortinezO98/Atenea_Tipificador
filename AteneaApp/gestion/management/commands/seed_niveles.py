# gestion/management/commands/seed_niveles.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Model
from typing import Any, Dict, List, Union

from gestion.models import Categoria  # ajusta si tu modelo está en otra app

"""
Seeder N1..N6 para Categoria.
- Crea/actualiza por (nombre, nivel, categoria_padre).
- No borra nada.
- Idempotente: puedes correrlo varias veces.
- Solo incluye en defaults los campos que EXISTEN en el modelo (p.ej. tipificacion).
"""

# --------------------------
# Utilidades de reflexión
# --------------------------
def model_has_field(model: Model, field_name: str) -> bool:
    return field_name in {f.name for f in model._meta.get_fields()}

# --------------------------
# Árbol de niveles (según tu Excel)
# Estructura:
#   { N1: { N2: { N3: { N4: { N5: [N6, ...] }}}}}
# También se permite:
#   { N1: { N2: [N3, ...] } }
# --------------------------
TREE: Dict[str, Any] = {
    "SICORE": {
        "ACTUALIZACIÓN HOJA DE VIDA": {
            "CORREO ELECTRÓNICO": ["CAMBIO DE CORREO"],
            "NOMBRES Y APELLIDOS": ["CAMBIO DE NOMBRE IDENTITARIO", "CORRECCIÓN DE NOMBRES Y/O APELLIDOS"],
            "TIPO Y NÚMERO DOCUMENTO": ["CAMBIO DE NÚMERO DE DOCUMENTO", "CAMBIO DE TIPO DE DOCUMENTO"],
            "ESTADO DE HOJA DE VIDA": [],
            "REBANCARIZACIÓN": ["CAMBIO DE BILLETERA", "MODIFICACIÓN DE NÚMERO DE TELEFONO TUTOR", "CAMBIO DE TUTOR"],
        },
        "ERROR EN PLATAFORMA": [
            "CAMBIO DE DATOS PERSONALES",
            "DATOS DEL ACUDIENTE",
            "DILIGENCIAMIENTO DE CAMPOS",
            "DOCUMENTOS REQUERIDOS",
            "NO PERMITE VALIDAR",
        ],
        "FORMULARIO INSCRIPCIONES": [
            "NO APARECE INTITUCIÓN DE BACHILLER",
            "NO APARECE LA IES",
            "NO PERMITE GUARDAR LA INSCRIPCIÓN",
            "NO PERMITE MODIFICAR LA PREFERENCIA",
            "NO PERMITE REGISTRO DE DATOS DE REBANCARIZACIÓN",
            "USUARIO INACTIVO",
        ],
        "INGRESO A SICORE": [
            "CONTRASEÑA INCORRECTA",
            "CORREO INCORRECTO",
            "DATOS NO CONCUERDAN CON LOS REGISTRADOS",
            "RESTABLECIMIENTO DE CONTRASEÑA",
            "USUARIO NO REGISTRADO",
        ],
    },

    "PROGRAMAS": {
        "JÓVENES A LA E": {
            "PASANTÍAS": [],
            "APOYO DE SOSTENIMIENTO": {
                "DISPERSIÓN": {
                    "ESTADO DE APOYO DE SOSTENIMIENTO": ["RECHAZADO", "PAGO PENDIENTE", "PAGO EXITOSO"]
                },
                "REINTEGRO APOYO ECONÓMICO": {
                    "DESISTIMIENTO",
                    "SEMESTRE NO CURSADO APLAZAMIENTO",
                    "UNIVERSIDAD NO FORMALIZA EL BENEFICIO",


                }
            },
            "BENEFICIOS": ["AUXILIO DE TRANSPORTE", "PAGO DE MATRICULA"],
            "FORMALIZACIÓN": ["CARTA DE COMPROMISO"],
            "CRONOGRAMA": [],
            "RESULTADOS": [],
            "MANUAL OPERATIVO": ["APLAZAMIENTO", "BOLSA DE CRÉDITOS", "CAMBIO DE RUTA", "DESISTIMIENTO", "HOMOLOGAR", "OFERTA IES", "REQUISITOS"],
            "JÓVENES A LA E Y JOVENES CON OPORTUNIDADES": {
                "MANUAL OPERATIVO":[],
                "APOYO DE SOSTENIMIENTO": {
                    "DISPERSIÓN": {
                        "ESTADO DE APOYO DE SOSTENIMIENTO",
                        "PAGO PENDIENTE", 
                        "PAGO EXITOSO",
                    }
                }
            },
        },
        "TALENTO CAPITAL": {
            "TALENTO CAPITAL JOVENES CON OPORTUNIDADES": ["INCRIPCIONES"],
            "CRONOGRAMA": [],
            "RESULTADOS": [],
            "MANUAL OPERATIVO": ["FORMALIZACIÓN", "OFERTA IES", "REQUISITOS"],
        },
        "LA U EN TU COLEGIO": {
            "APOYO DE SOSTENIMIENTO": {
                "DISPERSIÓN": {
                    "ESTADO DE APOYO DE SOSTENIMIENTO": ["RECHAZADO", "PAGO PENDIENTE", "PAGO EXITOSO"]
                }
            }
        },
    },

    "FONDOS": {
        "FEST ATENEA": {
            "MANUAL OPERATIVO": [],
            "FORMALIZACIÓN": [],
        },
        "FONDO FEST": {
            "PASANTÍAS": ["OFERTA PASANTÍAS", "CERTIFICADO DE PASANTIAS"],
            "CONDONACIÓN": [],
        },
        "TYT": {
            "INCRIPCIONES": [],
            "CONDONACIÓN": [],
            "MANUAL OPERATIVO": [],
        },
        "VÍCTIMA DE CONFLICTO ARMADO": {
            "APOYO DE SOSTENIMIENTO": {
                "DISPERSIÓN": {"ESTADO DE APOYO DE SOSTENIMIENTO": ["RECHAZADO", "PAGO PENDIENTE", "PAGO EXITOSO"]}
            },
            "CONDONACIÓN": [],
        },
        "ALIANZA BOGOTÁ EDUCADORA": {
            "MANUAL OPERATIVO": [],
            "APOYO DE SOSTENIMIENTO": {
                "DISPERSIÓN": {"ESTADO DE APOYO DE SOSTENIMIENTO": ["RECHAZADO", "PAGO PENDIENTE", "PAGO EXITOSO"]}
            },
        },
        "FONDOS GENERALES": {"MANUAL OPERATIVO": []},
        "FONDOS LOCALES": {"INFORMACIÓN GENERAL": []},
        "UNIVERSIDADES PÚBLICAS": {"MANUAL OPERATIVO": []},
    },

    "CIENCIA, TECNOLOGÍA E INNOVACIÓN": {
        "PROYECTOS ESTRATÉGICOS - CONVOCATORIAS": [
            "BANCK PRO",
            "CONVENIOS",
            "PRESUPUESTOS",
            "PROPUESTAS",
            "PROYECTO HEMA",
            "VINCULACIÓN CON LA ENTIDAD",
        ]
    },

    "PQRS": {
        "RADICACIONES": {
            "ERROR EN APLICATIVO": ["NO PERMITE ADJUNTAR ARCHIVOS"]
        },
        "PASO A PASO RADICACIÓN": [],
        "RESPUESTA DE RADICADO": [],
        "TIEMPOS DE RESPUESTA": [],
    },

    "ACADEMIA ATENEA": {
        "CURSOS": [],
        "ACCESO": [],
    },

    "INFORMACIÓN GENERAL": {
        "ASESORÍA": {
            "PRESENCIAL": {
                "HORARIOS DE ATENCIÓN": [],
                "PUNTOS DE ATENCIÓN": [],
                "AGENDAMIENTO": ["AGENDAR CITA", "CANCELAR CITA"],
            },
            "ATENCIÓN VIRTUAL LENGUA DE SEÑAS COLOMBIANA": {
                "VIDEOLLAMADA": {
                    "AGENDAMIENTO": []
                }
            },
        },
        "TEMAS DIFERENTES": [],
        "NOTIFICACIONES": [],
        "OFERTA LABORAL": [],
        "PROVEDORES": [],
        "PRÓXIMAS CONVOCATORIAS": [],
    },

    "NO EFECTIVA": {
        "FALLA DE RED": {"CAÍDA DE INTERACCIÓN": []},
        "INTERACCIÓN COLGADA": {
            "CIERRE DE CHAT CON GUION": [],
            "FINALIZA CHAT CIUDADANO":[],
            "FINALIZA LLAMADA CIUDADANO": [],
            "CIERRE LLAMADA CON GUION": [],
        },
        "INTERACCIÓN DE PRUEBA": [],
        "INTERACCIÓN EQUIVOCADA/BROMA": [],
        "INTERACCIÓN SIN AUDIO": [],
    },
}

# --------------------------
# Upsert de categorías
# --------------------------
def upsert_categoria(nombre: str, nivel: int, padre=None):
    """
    Crea/actualiza Categoria por (nombre, nivel, categoria_padre).
    Solo añade a defaults los campos que existan en el modelo.
    """
    defaults: Dict[str, Any] = {}
    if model_has_field(Categoria, 'tipificacion'):
        defaults['tipificacion'] = None  # legacy off

    # Si tu modelo SÍ tiene 'activo', se agregará; si no, no (evita el FieldError)
    if model_has_field(Categoria, 'activo'):
        defaults['activo'] = True

    obj, created = Categoria.objects.get_or_create(
        nombre=nombre.strip(),
        nivel=nivel,
        categoria_padre=padre,
        defaults=defaults
    )

    # Si existía con tipificación, y queremos desasociarla para niveles
    if model_has_field(Categoria, 'tipificacion') and getattr(obj, 'tipificacion_id', None):
        obj.tipificacion = None
        obj.save(update_fields=['tipificacion'])

    return obj, created

# --------------------------
# Recorrido recursivo
# --------------------------
def walk(node: Union[Dict[str, Any], List[Any], str], nivel: int, padre):
    """
    node:
      - dict: { "Hijo": subnode, ... }
      - list: ["Hijo1", "Hijo2", ...]  (hojas del nivel actual)
      - str : nombre de hoja (nivel actual)

    Límite: nivel 6 (N6). Todo lo que caiga por debajo se crea en N6.
    """
    if nivel >= 6:
        # Forzar cualquier hijo adicional como N6
        if isinstance(node, dict):
            for k in node.keys():
                upsert_categoria(k, 6, padre)
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, str):
                    upsert_categoria(item, 6, padre)
        elif isinstance(node, str):
            upsert_categoria(node, 6, padre)
        return

    if isinstance(node, dict):
        for nombre, sub in node.items():
            hijo, _ = upsert_categoria(nombre, nivel, padre)
            if isinstance(sub, (dict, list, str)):
                walk(sub, nivel + 1, hijo)

    elif isinstance(node, list):
        for nombre in node:
            if isinstance(nombre, str):
                upsert_categoria(nombre, nivel, padre)
            else:
                # En caso de mezcla rara (lista con dicts), procesar recursivo al mismo nivel
                walk(nombre, nivel, padre)

    elif isinstance(node, str):
        upsert_categoria(node, nivel, padre)

# --------------------------
# Management command
# --------------------------
class Command(BaseCommand):
    help = "Siembra la jerarquía N1..N6 en Categoria (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options):
        creados = 0
        actualizados_tip = 0

        for n1_nombre, sub in TREE.items():
            n1, was_created = upsert_categoria(n1_nombre, 1, None)
            if was_created:
                creados += 1
            walk(sub, 2, n1)

        # Pequeño resumen
        total_n1 = Categoria.objects.filter(nivel=1).count()
        total_n2 = Categoria.objects.filter(nivel=2).count()
        total_n3 = Categoria.objects.filter(nivel=3).count()
        total_n4 = Categoria.objects.filter(nivel=4).count()
        total_n5 = Categoria.objects.filter(nivel=5).count()
        total_n6 = Categoria.objects.filter(nivel=6).count()

        self.stdout.write(self.style.SUCCESS("✅ Seeder de niveles ejecutado correctamente."))
        self.stdout.write(f"N1: {total_n1} | N2: {total_n2} | N3: {total_n3} | N4: {total_n4} | N5: {total_n5} | N6: {total_n6}")
