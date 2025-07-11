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
        raise ValidationError(_("Invalid file format. Only PDF, JPG and PNG are allowed."))
    if value.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError(_("The file must not exceed 5MB."))

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
    EN_REVISION = "En Revisión", _("Under Review")
    APROBADO = "Aprobado", _("Approved")
    RECHAZADO = "Rechazado", _("Rejected")

class EstadoDocumento(models.TextChoices):
    EN_REVISION = "En Revisión", _("Under Review")
    APROBADO = "Aprobado", _("Approved")
    RECHAZADO = "Rechazado", _("Rejected")

def documento_estado_field():
    return models.CharField(
        max_length=20,
        choices=EstadoDocumento.choices,
        default=EstadoDocumento.EN_REVISION
    )

def documento_mensaje_field():
    return models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Document Rejection Message")
    )

class DocumentosEstudiante(models.Model):
    estudiante = models.OneToOneField(Estudiantes, on_delete=models.CASCADE, related_name="documentos")
    codigo_inscripcion = models.CharField(max_length=15, unique=True, blank=True, editable=False)

    passport_copy = models.FileField(
        upload_to='documentos_estudiantes/pasaporte_copy/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Passport Copy (Data Page and all signed/stamped/visa pages)")
    )
    passport_copy_estado = documento_estado_field()
    passport_copy_mensaje = documento_mensaje_field()

    previous_visa_refusal_letters = models.FileField(
        upload_to='documentos_estudiantes/visa_refusal/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Previous Visa Refusal Letters (if applicable)")
    )
    previous_visa_refusal_letters_estado = documento_estado_field()
    previous_visa_refusal_letters_mensaje = documento_mensaje_field()

    national_id_copy = models.FileField(
        upload_to='documentos_estudiantes/national_id/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("National ID Copy")
    )
    national_id_copy_estado = documento_estado_field()
    national_id_copy_mensaje = documento_mensaje_field()

    biometric_photos = models.FileField(
        upload_to='documentos_estudiantes/photos/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("2 Biometric Photos (35x45 size)")
    )
    biometric_photos_estado = documento_estado_field()
    biometric_photos_mensaje = documento_mensaje_field()

    police_clearance_certificates = models.FileField(
        upload_to='documentos_estudiantes/police_clearance/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Police Clearance Certificates")
    )
    police_clearance_certificates_estado = documento_estado_field()
    police_clearance_certificates_mensaje = documento_mensaje_field()

    travel_health_insurance = models.FileField(
        upload_to='documentos_estudiantes/health_insurance/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Travel Health Insurance")
    )
    travel_health_insurance_estado = documento_estado_field()
    travel_health_insurance_mensaje = documento_mensaje_field()

    enrollment_letter = models.FileField(
        upload_to='documentos_estudiantes/enrollment_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Enrollment Letter from SEDA")
    )
    enrollment_letter_estado = documento_estado_field()
    enrollment_letter_mensaje = documento_mensaje_field()

    booking_letter = models.FileField(
        upload_to='documentos_estudiantes/booking_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Booking Letter from SEDA")
    )
    booking_letter_estado = documento_estado_field()
    booking_letter_mensaje = documento_mensaje_field()

    payment_receipt = models.FileField(
        upload_to='documentos_estudiantes/payment_receipt/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Payment Receipt from SEDA")
    )
    payment_receipt_estado = documento_estado_field()
    payment_receipt_mensaje = documento_mensaje_field()

    diploma_translated = models.FileField(
        upload_to='documentos_estudiantes/diploma_translated/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Recent Diploma Translated into English")
    )
    diploma_translated_estado = documento_estado_field()
    diploma_translated_mensaje = documento_mensaje_field()

    transcript_translated = models.FileField(
        upload_to='documentos_estudiantes/transcript_translated/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Recent Transcript Translated into English")
    )
    transcript_translated_estado = documento_estado_field()
    transcript_translated_mensaje = documento_mensaje_field()

    student_letter = models.FileField(
        upload_to='documentos_estudiantes/student_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Student Letter from College (if applicable)")
    )
    student_letter_estado = documento_estado_field()
    student_letter_mensaje = documento_mensaje_field()

    payslips_last_3_months = models.FileField(
        upload_to='documentos_estudiantes/payslips/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Payslips for Last 3 Months (if employed)")
    )
    payslips_last_3_months_estado = documento_estado_field()
    payslips_last_3_months_mensaje = documento_mensaje_field()

    Applicants_translated_work_history = models.FileField(
        upload_to='documentos_estudiantes/Applicants_translated_work_history/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Applicant's Employment History")
    )
    Applicants_translated_work_history_estado = documento_estado_field()
    Applicants_translated_work_history_mensaje = documento_mensaje_field()

    supportive_certificate = models.FileField(
        upload_to='documentos_estudiantes/supportive_certificate/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Supportive Certificate or Reasons to Study English Abroad")
    )
    supportive_certificate_estado = documento_estado_field()
    supportive_certificate_mensaje = documento_mensaje_field()

    intention_letter = models.FileField(
        upload_to='documentos_estudiantes/intention_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Intention Letter")
    )
    intention_letter_estado = documento_estado_field()
    intention_letter_mensaje = documento_mensaje_field()

    reason_for_return = models.FileField(
        upload_to='documentos_estudiantes/reason_for_return/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Reason for Return")
    )
    reason_for_return_estado = documento_estado_field()
    reason_for_return_mensaje = documento_mensaje_field()
    
    financial_summary_form = models.FileField(
        upload_to='documentos_estudiantes/financial_summary/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Financial Summary Form")
    )
    financial_summary_form_estado = documento_estado_field()
    financial_summary_form_mensaje = documento_mensaje_field()
    
        
    sponsorship_letter = models.FileField(
        upload_to='documentos_estudiantes/sponsorship_letter/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("Sponsorship Letter (if applicable)")
    )
    sponsorship_letter_estado = documento_estado_field()
    sponsorship_letter_mensaje = documento_mensaje_field()

    bank_statement = models.FileField(
        upload_to='documentos_estudiantes/bank_statement/', 
        blank=True, 
        null=True, 
        validators=[validar_archivo],
        verbose_name=_("6 Months Bank Statement (Proof of 10,000 Euros)")
    )
    bank_statement_estado = documento_estado_field()
    bank_statement_mensaje = documento_mensaje_field()

    mensaje_rechazo = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Mensaje de Rechazo",
        help_text=_("Motivo del rechazo de la inscripción.")
    )
    
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    estado_inscripcion = models.CharField(
        max_length=20, 
        choices=EstadoInscripcion.choices, 
        default=EstadoInscripcion.EN_REVISION
    )
    
    necesita_patrocinio = models.BooleanField(default=False, verbose_name="Need sponsorship?")

    # Documentos de patrocinio (opcional, se validarán solo si necesita_patrocinio es True)
    id_patrocinador = models.FileField(
        upload_to='documentos_estudiantes/patrocinio/id/',
        blank=True,
        null=True,
        validators=[validar_archivo],
        verbose_name=_("Sponsor ID or passport")
    )
    id_patrocinador_estado = documento_estado_field()
    id_patrocinador_mensaje = documento_mensaje_field()

    carta_patrocinio = models.FileField(
        upload_to='documentos_estudiantes/patrocinio/carta/',
        blank=True,
        null=True,
        validators=[validar_archivo]
    )
    carta_patrocinio_estado = documento_estado_field()
    carta_patrocinio_mensaje = documento_mensaje_field()

    prueba_relacion = models.FileField(
        upload_to='documentos_estudiantes/patrocinio/relacion/',
        blank=True,
        null=True,
        validators=[validar_archivo]
    )
    prueba_relacion_estado = documento_estado_field()
    prueba_relacion_mensaje = documento_mensaje_field()

    estados_bancarios_patrocinador = models.FileField(
        upload_to='documentos_estudiantes/patrocinio/estado_bancario/',
        blank=True,
        null=True,
        validators=[validar_archivo],
        verbose_name=_("Bank statement (6 months)")
    )
    estados_bancarios_patrocinador_estado = documento_estado_field()
    estados_bancarios_patrocinador_mensaje = documento_mensaje_field()

    prueba_ingresos = models.FileField(
        upload_to='documentos_estudiantes/patrocinio/ingresos/',
        blank=True,
        null=True,
        validators=[validar_archivo],
        verbose_name=_("Proof of income")
    )
    prueba_ingresos_estado = documento_estado_field()
    prueba_ingresos_mensaje = documento_mensaje_field()

    detalles_empresa = models.FileField(
        upload_to='documentos_estudiantes/patrocinio/empresa/',
        blank=True,
        null=True,
        validators=[validar_archivo],
        verbose_name=_("Company documents (if applicable)")
    )
    detalles_empresa_estado = documento_estado_field()
    detalles_empresa_mensaje = documento_mensaje_field()


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
        documentos = [
            self.passport_copy,
            self.previous_visa_refusal_letters,
            self.national_id_copy,
            self.biometric_photos,
            self.police_clearance_certificates,
            self.travel_health_insurance,
            self.enrollment_letter,
            self.booking_letter,
            self.payment_receipt,
            self.diploma_translated,
            self.transcript_translated,
            self.student_letter,
            self.payslips_last_3_months,
            self.Applicants_translated_work_history,
            self.supportive_certificate,
            self.intention_letter,
            self.reason_for_return,
            self.financial_summary_form,
            self.bank_statement,
        ]
        
        patrocinio = []
        if self.necesita_patrocinio:
            patrocinio = [
                self.id_patrocinador,
                self.carta_patrocinio,
                self.prueba_relacion,
                self.estados_bancarios_patrocinador,
                self.prueba_ingresos,
                self.detalles_empresa,
            ]
            
        total_documentos = len(documentos) + (len(patrocinio) if self.necesita_patrocinio else 0)
        documentos_subidos = sum(bool(doc) for doc in documentos + patrocinio)
        
        if total_documentos == 0:
            return 0  # Por si acaso
        
        return int((documentos_subidos / total_documentos) * 100)

    def __str__(self):
        return f"Documentos de {self.estudiante.nombre} {self.estudiante.apellido}"

auditlog.register(Estudiantes)
auditlog.register(DocumentosEstudiante)