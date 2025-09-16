from .models import *

def RegistrarError(metodo, excepcion, request):
    try:
        RegistroError.objects.create(
            metodo=metodo,
            excepcion=excepcion,
            usuario= request.user if request.user.is_authenticated else None,
        )
    except Exception as e:
        print(f"Error al registrar la excepción: {e}")


def get_ciudadano_anonimo():
    tipo = TipoIdentificacion.objects.first()
    for doc in ("9999999", "9999"):
        anon = Ciudadano.objects.filter(numero_identificacion=doc).first()
        if anon:
            return anon
    anon, _ = Ciudadano.objects.get_or_create(
        numero_identificacion="9999999",
        defaults=dict(
            tipo_identificacion=tipo,
            nombre="ANONIMO", correo="", telefono="",
            direccion_residencia="", pais=None, ciudad=""
        )
    )
    return anon