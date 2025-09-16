from django.core.management.base import BaseCommand
from gestion.models import PreguntaEncuesta

class Command(BaseCommand):
    help = "Carga las preguntas iniciales de la encuesta de satisfacción"

    def handle(self, *args, **options):
        preguntas = [
            ("¿Cuál es su satisfacción con la atención recibida?", "escala"),
            ("¿Considera que el asesor fue amable y proactivo durante la interacción?", "si_no"),
            ("¿La asesoría recibida contribuye en la solución de su requerimiento?", "si_no"),
            ("¿El tiempo de espera para ser atendido fue oportuno?", "si_no"),
        ]

        for i, (texto, tipo) in enumerate(preguntas, start=1):
            obj, created = PreguntaEncuesta.objects.get_or_create(
                texto=texto,
                defaults={"tipo": tipo, "orden": i}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Pregunta creada: {texto}"))
            else:
                self.stdout.write(self.style.WARNING(f"Ya existía: {texto}"))
