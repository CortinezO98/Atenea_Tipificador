from django.core.management.base import BaseCommand
from django.db import transaction
from gestion.models import Delito

class Command(BaseCommand):
    help = 'Carga delitos de ejemplo en la base de datos'

    def handle(self, *args, **kwargs):
        delitos_data = [
            # Delitos contra la vida y la integridad personal
            {'codigo': 'L103-1', 'nombre': 'Homicidio', 'descripcion': 'El que matare a otro'},
            {'codigo': 'L103-2', 'nombre': 'Feminicidio', 'descripcion': 'Quien causare la muerte a una mujer por su condición de ser mujer'},
            {'codigo': 'L111', 'nombre': 'Lesiones Personales', 'descripcion': 'El que cause a otro daño en el cuerpo o en la salud'},
            
            # Delitos contra la libertad
            {'codigo': 'L168', 'nombre': 'Secuestro Simple', 'descripcion': 'El que arrebate, sustraiga, retenga u oculte a una persona'},
            {'codigo': 'L169', 'nombre': 'Secuestro Extorsivo', 'descripcion': 'El que arrebate, sustraiga, retenga u oculte a una persona con el propósito de exigir rescate'},
            {'codigo': 'L188', 'nombre': 'Trata de Personas', 'descripcion': 'El que capte, traslade, acoja o reciba a una persona'},
            
            # Delitos contra la libertad, integridad y formación sexuales
            {'codigo': 'L205', 'nombre': 'Acceso Carnal Violento', 'descripcion': 'El que realice acceso carnal con otra persona mediante violencia'},
            {'codigo': 'L206', 'nombre': 'Acto Sexual Violento', 'descripcion': 'El que realice en otra persona acto sexual diverso al acceso carnal mediante violencia'},
            {'codigo': 'L208', 'nombre': 'Acceso Carnal o Acto Sexual en Persona Menor de 14 Años', 'descripcion': 'El que realice acceso carnal o acto sexual con persona menor de catorce años'},
            {'codigo': 'L213', 'nombre': 'Inducción a la Prostitución', 'descripcion': 'El que con ánimo de lucro induzca al comercio carnal'},
            
            # Delitos contra la familia
            {'codigo': 'L229', 'nombre': 'Violencia Intrafamiliar', 'descripcion': 'El que maltrate física o psicológicamente a cualquier miembro de su núcleo familiar'},
            {'codigo': 'L230', 'nombre': 'Mendicidad', 'descripcion': 'El que induzca, facilite, utilice, constriña, promueva o instrumentalice a un menor de edad'},
            
            # Delitos contra el patrimonio económico
            {'codigo': 'L239', 'nombre': 'Hurto Simple', 'descripcion': 'El que se apodere de una cosa mueble ajena'},
            {'codigo': 'L240', 'nombre': 'Hurto Calificado', 'descripcion': 'La pena será de prisión cuando el hurto se cometa con violencia'},
            {'codigo': 'L244', 'nombre': 'Extorsión', 'descripcion': 'El que constriña a otro a hacer, tolerar u omitir alguna cosa'},
            {'codigo': 'L265', 'nombre': 'Estafa', 'descripcion': 'El que obtenga provecho ilícito para sí o para un tercero'},
            
            # Delitos contra la seguridad pública
            {'codigo': 'L340', 'nombre': 'Fabricación, Tráfico y Porte de Armas', 'descripcion': 'El que sin permiso de autoridad competente importe, fabrique, repare, almacene, conserve, adquiera, suministre, porte o use armas'},
            {'codigo': 'L376', 'nombre': 'Tráfico, Fabricación o Porte de Estupefacientes', 'descripcion': 'El que sin permiso de autoridad competente introduzca al país, así sea en tránsito o saque de él, transporte, lleve consigo, almacene, conserve, elabore, venda, ofrezca, adquiera, financie o suministre a cualquier título droga que produzca dependencia'},
            
            # Delitos contra la administración pública
            {'codigo': 'L397', 'nombre': 'Peculado por Apropiación', 'descripcion': 'El servidor público que se apropie en provecho suyo o de un tercero de bienes del Estado'},
            {'codigo': 'L404', 'nombre': 'Cohecho Propio', 'descripcion': 'El servidor público que reciba para sí o para otro dinero u otra utilidad'},
            {'codigo': 'L433', 'nombre': 'Abuso de Autoridad por Acto Arbitrario e Injusto', 'descripcion': 'El servidor público que abusando de su cargo o de sus funciones cometa acto arbitrario e injusto'},
            
            # Delitos informáticos y conexos
            {'codigo': 'L269A', 'nombre': 'Acceso Abusivo a un Sistema Informático', 'descripción': 'El que, sin autorización o por fuera de lo acordado, acceda en todo o en parte a un sistema informático'},
            {'codigo': 'L269B', 'nombre': 'Obstaculización Ilegítima de Sistema Informático', 'descripcion': 'El que, sin estar facultado para ello, impida u obstaculice el funcionamiento o el acceso normal a un sistema informático'},
            
            # Otros delitos comunes
            {'codigo': 'L365', 'nombre': 'Amenazas', 'descripcion': 'El que por cualquier medio apto para difundir el pensamiento atemorice o amenace a otro'},
            {'codigo': 'L220', 'nombre': 'Injuria', 'descripcion': 'El que haga a otro imputaciones deshonrosas'},
            {'codigo': 'L221', 'nombre': 'Calumnia', 'descripcion': 'El que impute falsamente a otro una conducta típica'},
            {'codigo': 'L177', 'nombre': 'Tortura', 'descripcion': 'El que inflija a una persona dolores o sufrimientos graves'},
        ]

        try:
            with transaction.atomic():
                for delito_data in delitos_data:
                    delito, created = Delito.objects.get_or_create(
                        codigo=delito_data['codigo'],
                        defaults={
                            'nombre': delito_data['nombre'],
                            'descripcion': delito_data.get('descripcion', ''),
                            'activo': True
                        }
                    )
                    if created:
                        self.stdout.write(f"✅ Delito creado: {delito.codigo} - {delito.nombre}")
                    else:
                        self.stdout.write(f"⚠️ Delito ya existe: {delito.codigo} - {delito.nombre}")
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Proceso completado. Total delitos en BD: {Delito.objects.count()}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )