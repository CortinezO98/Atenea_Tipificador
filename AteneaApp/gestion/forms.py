from django import forms
from .models import PreguntaEncuesta

ESCALA_CHOICES = [(str(i), str(i)) for i in range(1, 6)]
SINO_CHOICES = [("Sí", "Sí"), ("No", "No")]

def build_encuesta_form(preguntas):
    """
    Devuelve una subclase de forms.Form con un campo por pregunta.
    El nombre del campo será q_<id>.
    """
    fields = {}
    for p in preguntas:
        name = f"q_{p.id}"
        if p.tipo == "escala":
            fields[name] = forms.ChoiceField(
                label=p.texto,
                choices=ESCALA_CHOICES,
                widget=forms.RadioSelect,
                required=True
            )
        else:  
            fields[name] = forms.ChoiceField(
                label=p.texto,
                choices=SINO_CHOICES,
                widget=forms.RadioSelect,
                required=True
            )

    return type("DynamicEncuestaForm", (forms.Form,), fields)
