# Marca evaluaciones anónimas y (opcionalmente) congela contactos actuales
# Archivo: gestion/migrations/0006_eval_snapshot_anon.py

from django.db import migrations
from django.db.models import Q


def mark_anon(apps, schema_editor):
    """
    Marca como anónimas todas las Evaluaciones cuyo Ciudadano tiene
    número_identificacion 9999 o 9999999.
    """
    Evaluacion = apps.get_model('gestion', 'Evaluacion')
    (Evaluacion.objects
        .filter(ciudadano__numero_identificacion__in=['9999', '9999999'])
        .update(es_anonimo=True)
    )


def snapshot_contacts(apps, schema_editor):
    """
    Copia a nivel de Evaluacion los contactos actuales SOLO cuando:
      - es_anonimo=True
      - y los 3 campos contacto_* están vacíos (NULL o '')

    Nota: A esta altura, el modelo Ciudadano ya NO tiene telefono_inconcer
    (se eliminó en 0005). Por tanto, dejamos contacto_telefono_inconcer en blanco.
    """
    Evaluacion = apps.get_model('gestion', 'Evaluacion')

    null_or_blank_correo   = Q(contacto_correo__isnull=True) | Q(contacto_correo='')
    null_or_blank_telefono = Q(contacto_telefono__isnull=True) | Q(contacto_telefono='')
    null_or_blank_inconcer = Q(contacto_telefono_inconcer__isnull=True) | Q(contacto_telefono_inconcer='')

    qs = (
        Evaluacion.objects
        .filter(es_anonimo=True)
        .filter(null_or_blank_correo, null_or_blank_telefono, null_or_blank_inconcer)
        .select_related('ciudadano')
    )

    for e in qs.iterator():
        ciu = getattr(e, 'ciudadano', None)
        e.contacto_correo = (getattr(ciu, 'correo', '') or '') if e.ciudadano_id else ''
        e.contacto_telefono = (getattr(ciu, 'telefono', '') or '') if e.ciudadano_id else ''
        e.contacto_telefono_inconcer = e.contacto_telefono_inconcer or ''
        e.save(update_fields=['contacto_correo', 'contacto_telefono', 'contacto_telefono_inconcer'])


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_remove_ciudadano_telefono_inconcer'),
    ]

    operations = [
        migrations.RunPython(mark_anon, migrations.RunPython.noop),
        migrations.RunPython(snapshot_contacts, migrations.RunPython.noop),
    ]
