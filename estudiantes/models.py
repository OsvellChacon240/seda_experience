import os
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django_countries.fields import CountryField
from usuarios.models import CustomUser
from auditlog.registry import auditlog
from django.utils.translation import gettext_lazy as _

# Función para validar formato y tamaño de archivo
def validar_archivo(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if ext not in valid_extensions:
        raise ValidationError("Formato de archivo no válido. Solo se permiten PDF, JPG y PNG.")
    if value.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("El archivo no debe superar los 5MB.")

# Función para generar un código único de inscripción
def generar_codigo_inscripcion(pasaporte):
    unique_part = uuid.uuid4().hex[:5].upper()  # 5 caracteres aleatorios
    return f"{pasaporte}-{unique_part}"

class Estudiantes(CustomUser): 
    rol = models.CharField(max_length=20, default='Estudiante')
    nacionalidad = CountryField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.nacionalidad})"
    
class EstadoInscripcion(models.TextChoices):
    EN_REVISION = "En Revisión", "En Revisión"
    APROBADO = "Aprobado", "Aprobado"
    RECHAZADO = "Rechazado", "Rechazado"

class DocumentosEstudiante(models.Model):
    estudiante = models.OneToOneField(Estudiantes, on_delete=models.CASCADE, related_name="documentos")
    codigo_inscripcion = models.CharField(max_length=15, unique=True, blank=True, editable=False)

    # Documentos requeridos
    pasaporte = models.FileField(upload_to='documentos_estudiantes/pasaporte/', blank=True, null=True, validators=[validar_archivo])
    documento_identidad = models.FileField(upload_to='documentos_estudiantes/identidad/', blank=True, null=True, validators=[validar_archivo])
    antecedentes_penales = models.FileField(upload_to='documentos_estudiantes/antecedentes/', blank=True, null=True, validators=[validar_archivo])
    seguro_medico = models.FileField(upload_to='documentos_estudiantes/seguro/', blank=True, null=True, validators=[validar_archivo])
    carta_inscripcion = models.FileField(upload_to='documentos_estudiantes/carta_inscripcion/', blank=True, null=True, validators=[validar_archivo])
    recibo_pago = models.FileField(upload_to='documentos_estudiantes/pago/', blank=True, null=True, validators=[validar_archivo])
    diploma_traducido = models.FileField(upload_to='documentos_estudiantes/diploma/', blank=True, null=True, validators=[validar_archivo])
    transcripcion_traducida = models.FileField(upload_to='documentos_estudiantes/transcripcion/', blank=True, null=True, validators=[validar_archivo])
    carta_intencion = models.FileField(upload_to='documentos_estudiantes/carta_intencion/', blank=True, null=True, validators=[validar_archivo])
    resumen_financiero = models.FileField(upload_to='documentos_estudiantes/resumen_financiero/', blank=True, null=True, validators=[validar_archivo])
    extracto_bancario = models.FileField(upload_to='documentos_estudiantes/extracto_bancario/', blank=True, null=True, validators=[validar_archivo])

    mensaje_rechazo = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Mensaje de Rechazo",
        help_text="Motivo del rechazo de la inscripción."
    )
    
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    estado_inscripcion = models.CharField(
        max_length=20, 
        choices=EstadoInscripcion.choices, 
        default=EstadoInscripcion.EN_REVISION
    )
    
    necesita_patrocinio = models.BooleanField(default=False, verbose_name="Need sponsorship?")

    # Documentos de patrocinio (opcional, se validarán solo si necesita_patrocinio es True)
    id_patrocinador = models.FileField(upload_to='documentos_estudiantes/patrocinio/id/', blank=True, null=True, validators=[validar_archivo], verbose_name="ID o pasaporte del patrocinador")
    carta_patrocinio = models.FileField(upload_to='documentos_estudiantes/patrocinio/carta/', blank=True, null=True, validators=[validar_archivo])
    prueba_relacion = models.FileField(upload_to='documentos_estudiantes/patrocinio/relacion/', blank=True, null=True, validators=[validar_archivo])
    estados_bancarios_patrocinador = models.FileField(upload_to='documentos_estudiantes/patrocinio/estado_bancario/', blank=True, null=True, validators=[validar_archivo], verbose_name="Estado bancario (6 meses)")
    prueba_ingresos = models.FileField(upload_to='documentos_estudiantes/patrocinio/ingresos/', blank=True, null=True, validators=[validar_archivo], verbose_name="Prueba de ingresos")
    detalles_empresa = models.FileField(upload_to='documentos_estudiantes/patrocinio/empresa/', blank=True, null=True, validators=[validar_archivo], verbose_name="Documentos de empresa (si aplica)")

    
    class Meta:
        permissions = [
            ("view_documentos_pendientes", "Puede ver documentos pendientes"),
            ("approve_documentos", "Puede aprobar documentos"),
            ("reject_documentos", "Puede rechazar documentos"),
        ]
        
    def clean(self):
            """
            Construye un diccionario de datos a partir de los atributos del modelo y,
            si necesita patrocinio, verifica que se hayan proporcionado los campos obligatorios.
            En caso de error, lanza una ValidationError con un diccionario de errores.
            """
            # Construimos un diccionario con los valores actuales de los campos
            cleaned_data = {}
            for field in self._meta.fields:
                # Usamos el nombre del campo y obtenemos su valor
                cleaned_data[field.name] = getattr(self, field.name)
            
            # Validamos si necesita patrocinio
            if cleaned_data.get('necesita_patrocinio'):
                campos_requeridos = [
                    'id_patrocinador',
                    'carta_patrocinio',
                    'prueba_relacion',
                    'estados_bancarios_patrocinador',
                    'prueba_ingresos',
                    'detalles_empresa',
                ]
                errors = {}
                for campo in campos_requeridos:
                    if not cleaned_data.get(campo):
                        errors[campo] = _("Este campo es obligatorio si necesita patrocinio.")
                if errors:
                    raise ValidationError(errors)
            # No es necesario devolver cleaned_data en clean(), solo lanzar error si hay

    def save(self, *args, **kwargs):
        if not self.codigo_inscripcion:
            self.codigo_inscripcion = generar_codigo_inscripcion(self.estudiante.pasaporte)
        super().save(*args, **kwargs)

    def calcular_progreso(self):
        """
        Calcula el porcentaje de documentos subidos.
        """
        total_documentos = 11  # Número total de documentos requeridos
        if self.necesita_patrocinio:
            total_documentos += 6  # Añadir los documentos de patrocinio si es necesario
        documentos_subidos = sum([
            bool(self.pasaporte),
            bool(self.documento_identidad),
            bool(self.antecedentes_penales),
            bool(self.seguro_medico),
            bool(self.carta_inscripcion),
            bool(self.recibo_pago),
            bool(self.diploma_traducido),
            bool(self.transcripcion_traducida),
            bool(self.carta_intencion),
            bool(self.resumen_financiero),
            bool(self.extracto_bancario),
            bool(self.id_patrocinador) if self.necesita_patrocinio else False,
            bool(self.carta_patrocinio) if self.necesita_patrocinio else False,
            bool(self.prueba_relacion) if self.necesita_patrocinio else False,
            bool(self.estados_bancarios_patrocinador) if self.necesita_patrocinio else False,
            bool(self.prueba_ingresos) if self.necesita_patrocinio else False,
            bool(self.detalles_empresa) if self.necesita_patrocinio else False,
        ])
        return int((documentos_subidos / total_documentos) * 100)


    def __str__(self):
        return f"Documentos de {self.estudiante.nombre} {self.estudiante.apellido}"

auditlog.register(Estudiantes)
auditlog.register(DocumentosEstudiante)