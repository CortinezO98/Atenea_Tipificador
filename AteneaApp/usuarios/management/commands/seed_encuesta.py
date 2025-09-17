from django.core.management.base import BaseCommand
from gestion.models import PreguntaEncuesta

class Command(BaseCommand):
    help = "Carga las preguntas iniciales de la encuesta de satisfacción (versión Chat ATENEA)"

    def handle(self, *args, **options):
        preguntas = [
            (1, "¿Cuál es su satisfacción con la atención recibida?", "escala"),
            (2, "¿Considera que el asesor fue amable y proactivo durante la interacción?", "si_no"),
            (3, "¿La asesoría recibida contribuye en la solución de su requerimiento?", "si_no"),
            (4, "¿El tiempo de espera para ser atendido fue oportuno?", "si_no"),
        ]

        creadas = 0
        for orden, texto, tipo in preguntas:
            obj, created = PreguntaEncuesta.objects.get_or_create(
                texto=texto, defaults={"tipo": tipo, "orden": orden}
            )
            if not created:
                obj.tipo = tipo
                obj.orden = orden
                obj.save()
            creadas += int(created)

        self.stdout.write(self.style.SUCCESS(f"Preguntas listas. Nuevas creadas: {creadas}"))
