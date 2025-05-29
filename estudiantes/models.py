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
    rol = models.CharField(max_length=20, default=_('Estudiante'))
    nacionalidad = CountryField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.nacionalidad})"
    
class EstadoInscripcion(models.TextChoices):
    EN_REVISION = "En Revisión", _("En Revisión")
    APROBADO = "Aprobado", _("Aprobado")
    RECHAZADO = "Rechazado", _("Rechazado")
class DocumentosEstudiante(models.Model):
    estudiante = models.OneToOneField(Estudiantes, on_delete=models.CASCADE, related_name="documentos")
    codigo_inscripcion = models.CharField(max_length=15, unique=True, blank=True, editable=False)

    passport_copy = models.FileField(
        upload_to='documentos_estudiantes/pasaporte_copy/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Passport Copy (Data Page and all signed/stamped/visa pages)"
    )
    previous_visa_refusal_letters = models.FileField(
        upload_to='documentos_estudiantes/visa_refusal/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Previous Visa Refusal Letters (if applicable)"
    )
    national_id_copy = models.FileField(
        upload_to='documentos_estudiantes/national_id/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="National ID Copy"
    )
    biometric_photos = models.FileField(
        upload_to='documentos_estudiantes/photos/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="2 Biometric Photos (35x45 size)"
    )
    police_clearance_certificates = models.FileField(
        upload_to='documentos_estudiantes/police_clearance/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Police Clearance Certificates"
    )
    travel_health_insurance = models.FileField(
        upload_to='documentos_estudiantes/health_insurance/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Travel Health Insurance"
    )
    enrollment_letter = models.FileField(
        upload_to='documentos_estudiantes/enrollment_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Enrollment Letter from SEDA"
    )
    booking_letter = models.FileField(
        upload_to='documentos_estudiantes/booking_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Booking Letter from SEDA"
    )
    payment_receipt = models.FileField(
        upload_to='documentos_estudiantes/payment_receipt/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Payment Receipt from SEDA"
    )
    diploma_translated = models.FileField(
        upload_to='documentos_estudiantes/diploma_translated/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Recent Diploma Translated into English"
    )
    transcript_translated = models.FileField(
        upload_to='documentos_estudiantes/transcript_translated/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Recent Transcript Translated into English"
    )
    student_letter = models.FileField(
        upload_to='documentos_estudiantes/student_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Student Letter from College (if applicable)"
    )
    payslips_last_3_months = models.FileField(
        upload_to='documentos_estudiantes/payslips/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Payslips for Last 3 Months (if employed)"
    )
    Applicants_translated_work_history = models.FileField(
        upload_to='documentos_estudiantes/Applicants_translated_work_history/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Applicant's Employment History"
    )
    supportive_certificate = models.FileField(
        upload_to='documentos_estudiantes/supportive_certificate/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Supportive Certificate or Reasons to Study English Abroad"
    )
    intention_letter = models.FileField(
        upload_to='documentos_estudiantes/intention_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Intention Letter"
    )
    reason_for_return = models.FileField(
        upload_to='documentos_estudiantes/reason_for_return/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Reason for Return"
    )
    
    financial_summary_form = models.FileField(
        upload_to='documentos_estudiantes/financial_summary/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Financial Summary Form"
    )
    
        
    sponsorship_letter = models.FileField(
        upload_to='documentos_estudiantes/sponsorship_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Sponsorship Letter (if applicable)"
    )

    visa_application_form = models.FileField(
        upload_to='documentos_estudiantes/visa_application/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="Online Visa Application Form and Its Summary"
    )
    bank_statement = models.FileField(
        upload_to='documentos_estudiantes/bank_statement/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name="6 Months Bank Statement (Proof of 10,000 Euros)"
    )

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

    @property
    def tiene_patrocinio(self):
        return self.necesita_patrocinio

    def detalles_patrocinio(self):
        """
        Devuelve un diccionario con los detalles de los documentos de patrocinio si existen.
        """
        if not self.tiene_patrocinio:
            return None
        return {
            "id_patrocinador": self.id_patrocinador,
            "carta_patrocinio": self.carta_patrocinio,
            "prueba_relacion": self.prueba_relacion,
            "estados_bancarios_patrocinador": self.estados_bancarios_patrocinador,
            "prueba_ingresos": self.prueba_ingresos,
            "detalles_empresa": self.detalles_empresa,
            "sponsorship_letter": getattr(self, "sponsorship_letter", None),
        }

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
        total_documentos = 20  # Número total de documentos requeridos
        if self.necesita_patrocinio:
            total_documentos += 6  # Añadir los documentos de patrocinio si es necesario
        documentos_subidos = sum([
            bool(self.passport_copy),
            bool(self.previous_visa_refusal_letters),
            bool(self.national_id_copy),
            bool(self.biometric_photos),
            bool(self.police_clearance_certificates),
            bool(self.travel_health_insurance),
            bool(self.enrollment_letter),
            bool(self.booking_letter),
            bool(self.payment_receipt),
            bool(self.diploma_translated),
            bool(self.transcript_translated),
            bool(self.student_letter),
            bool(self.payslips_last_3_months),
            bool(self.Applicants_translated_work_history),
            bool(self.supportive_certificate),
            bool(self.intention_letter),
            bool(self.reason_for_return),
            bool(self.financial_summary_form),
            bool(self.visa_application_form),
            bool(self.bank_statement),
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