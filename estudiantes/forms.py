from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import date
from .models import *
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import gettext_lazy as _
import re

class EstudiantesRegistroForm(UserCreationForm):
    class Meta:
        model = Estudiantes
        fields = ['nombre', 'apellido', 'email', 'pasaporte', 'genero', 'telefono', 'direccion', 'fecha_nacimiento', 'foto_perfil', 'nacionalidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'pasaporte': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'nacionalidad': CountrySelectWidget(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': _("Nombre"),
            'apellido': _("Apellido"),
            'email': _("Correo Electrónico"),
            'pasaporte': _("Número de Pasaporte"),
            'genero': _("Género"),
            'telefono': _("Teléfono"),
            'direccion': _("Dirección"),
            'fecha_nacimiento': _("Fecha de Nacimiento"),
            'foto_perfil': _("Foto de Perfil"),
            'nacionalidad': _("Nacionalidad"),
        }

    # Validación para la fecha de nacimiento (debe ser mayor de 16 años)
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if not fecha_nacimiento:
            raise ValidationError(_("La fecha de nacimiento es obligatoria."))
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad < 16:
            raise ValidationError(_("El estudiante debe tener al menos 16 años."))
        return fecha_nacimiento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Este correo electrónico ya está registrado."))
        return email
    
    # Validación personalizada para el pasaporte
    def clean_pasaporte(self):
        pasaporte = self.cleaned_data.get('pasaporte')
        if Estudiantes.objects.filter(pasaporte=pasaporte).exists():
            raise ValidationError(_("Ya existe un estudiante con este pasaporte."))
        return pasaporte

    # Validación personalizada para el teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validar formato internacional con prefijo de país, sin espacios, guiones o paréntesis
            if not re.match(r'^\+\d{1,4}\d{7,15}$', telefono):
                raise ValidationError(_(
                    "El número de teléfono debe estar en formato internacional, comenzando con '+' seguido del prefijo del país y el número, sin espacios, guiones o paréntesis. Ejemplo: +584147080725 o +14155552671."
                ))
        return telefono

    # Guardar usuario con contraseña encriptada
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.rol = 'Estudiante'  # Asegurar que el rol se mantenga como estudiante
        if commit:
            user.save()
        return user

class EstudiantesActualizacionForm(forms.ModelForm):
    class Meta:
        model = Estudiantes
        fields = ['nombre', 'apellido', 'email', 'pasaporte', 'genero', 'telefono', 'direccion', 'status', 'foto_perfil', 'nacionalidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'pasaporte': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'nacionalidad': CountrySelectWidget(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': _("Nombre"),
            'apellido': _("Apellido"),
            'email': _("Correo Electrónico"),
            'pasaporte': _("Número de Pasaporte"),
            'genero': _("Género"),
            'telefono': _("Teléfono"),
            'direccion': _("Dirección"),
            'status': _("Estado"),
            'foto_perfil': _("Foto de Perfil"),
            'nacionalidad': _("Nacionalidad"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que el valor actual de nacionalidad se mantenga
        if self.instance and self.instance.nacionalidad:
            self.fields['nacionalidad'].initial = self.instance.nacionalidad

    # Validación personalizada para el pasaporte
    def clean_pasaporte(self):
        pasaporte = self.cleaned_data.get('pasaporte')
        if Estudiantes.objects.filter(pasaporte=pasaporte).exclude(id=self.instance.id).exists():
            raise ValidationError(_("Ya existe un estudiante con este pasaporte."))
        return pasaporte

    # Validación personalizada para el teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validar formato internacional con prefijo de país, sin espacios, guiones o paréntesis
            if not re.match(r'^\+\d{1,4}\d{7,15}$', telefono):
                raise ValidationError(_(
                    "El número de teléfono debe estar en formato internacional, comenzando con '+' seguido del prefijo del país y el número, sin espacios, guiones o paréntesis. Ejemplo: +584147080725 o +14155552671."
                ))
        return telefono

    def save(self, commit=True):
        # Guardamos el objeto sin modificar la contraseña
        estudiante = super().save(commit=False)
        if commit:
            estudiante.save()
        return estudiante
    
class DocumentosEstudianteForm(forms.ModelForm):
    class Meta:
        model = DocumentosEstudiante
        fields = [
            'passport_copy', 'previous_visa_refusal_letters', 'national_id_copy', 'biometric_photos',
            'police_clearance_certificates', 'travel_health_insurance', 'enrollment_letter', 'booking_letter',
            'payment_receipt', 'diploma_translated', 'transcript_translated', 'student_letter',
            'payslips_last_3_months', 'Applicants_translated_work_history', 'supportive_certificate', 'intention_letter',
            'reason_for_return', 'financial_summary_form', 'visa_application_form', 'bank_statement',
            'necesita_patrocinio', 'id_patrocinador', 'carta_patrocinio', 'prueba_relacion',
            'estados_bancarios_patrocinador', 'prueba_ingresos', 'detalles_empresa', 'sponsorship_letter',
        ]

        widgets = {
            field: forms.ClearableFileInput(attrs={
                'class': 'form-control file-input',
                'data-browse-text': _("Seleccionar archivo"),  # Texto para el botón de selección
                'data-no-file-text': _("Ningún archivo seleccionado")  # Texto cuando no hay archivo seleccionado
            })
            for field in [
                'passport_copy', 'previous_visa_refusal_letters', 'national_id_copy', 'biometric_photos',
                'police_clearance_certificates', 'travel_health_insurance', 'enrollment_letter', 'booking_letter',
                'payment_receipt', 'diploma_translated', 'transcript_translated', 'student_letter',
                'payslips_last_3_months', 'Applicants_translated_work_history', 'supportive_certificate', 'intention_letter',
                'reason_for_return', 'financial_summary_form', 'visa_application_form', 'bank_statement',
                'id_patrocinador', 'carta_patrocinio', 'prueba_relacion',
                'estados_bancarios_patrocinador', 'prueba_ingresos', 'detalles_empresa', 'sponsorship_letter',
            ]
        }

        # Usamos un select en lugar de un checkbox para el campo de patrocinio
        widgets['necesita_patrocinio'] = forms.Select(choices=[
            (True, _('Sí')),
            (False, _('No')),
        ], attrs={'class': 'form-control'})

        labels = {
            'passport_copy': _("Passport Copy (Data Page and all signed/stamped/visa pages)"),
            'previous_visa_refusal_letters': _("Previous Visa Refusal Letters (if applicable)"),
            'national_id_copy': _("National ID Copy"),
            'biometric_photos': _("2 Biometric Photos (35x45 size)"),
            'police_clearance_certificates': _("Police Clearance Certificates"),
            'travel_health_insurance': _("Travel Health Insurance"),
            'enrollment_letter': _("Enrollment Letter from SEDA"),
            'booking_letter': _("Booking Letter from SEDA"),
            'payment_receipt': _("Payment Receipt from SEDA"),
            'diploma_translated': _("Recent Diploma Translated into English"),
            'transcript_translated': _("Recent Transcript Translated into English"),
            'student_letter': _("Student Letter from College (if applicable)"),
            'payslips_last_3_months': _("Payslips for Last 3 Months (if employed)"),
            'Applicants_translated_work_history': _("Applicant's Translated Work History"),
            'supportive_certificate': _("Supportive Certificate or Reasons to Study English Abroad"),
            'intention_letter': _("Intention Letter"),
            'reason_for_return': _("Reason for Return to Home Country"),
            'financial_summary_form': _("Financial Summary Form"),
            'visa_application_form': _("Online Visa Application Form and Its Summary"),
            'bank_statement': _("6 Months Bank Statement (Proof of 10,000 Euros)"),
            'necesita_patrocinio': _("¿Necesita patrocinio?"),
            'id_patrocinador': _("ID o Pasaporte del Patrocinador"),
            'carta_patrocinio': _("Carta de Patrocinio"),
            'prueba_relacion': _("Prueba de Relación"),
            'estados_bancarios_patrocinador': _("Estado Bancario del Patrocinador (6 meses)"),
            'prueba_ingresos': _("Prueba de Ingresos del Patrocinador"),
            'detalles_empresa': _("Documentos de Empresa del Patrocinador"),
            'sponsorship_letter': _("Carta de Patrocinio Adicional"),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            file_fields = [
                'passport_copy', 'previous_visa_refusal_letters', 'national_id_copy', 'biometric_photos',
                'police_clearance_certificates', 'travel_health_insurance', 'enrollment_letter', 'booking_letter',
                'payment_receipt', 'diploma_translated', 'transcript_translated', 'student_letter',
                'payslips_last_3_months', 'Applicants_translated_work_history', 'supportive_certificate', 'intention_letter',
                'financial_summary_form', 'visa_application_form', 'bank_statement',
                'id_patrocinador', 'carta_patrocinio', 'prueba_relacion',
                'estados_bancarios_patrocinador', 'prueba_ingresos', 'detalles_empresa', 'sponsorship_letter',
            ]
            for field in file_fields:
                val = getattr(instance, field)
                if val:  # Si ya existe un archivo para el campo...
                    # Agrega el atributo data-uploaded="true" al widget
                    if field in self.fields:
                        self.fields[field].widget.attrs.update({'data-uploaded': 'true'})

    def clean(self):
        cleaned_data = super().clean() or {}
        # Convertir a booleano si se pasa como string
        necesita_raw = cleaned_data.get('necesita_patrocinio')
        if isinstance(necesita_raw, str):
            necesita_patrocinio = necesita_raw == "True"
            cleaned_data['necesita_patrocinio'] = necesita_patrocinio
        else:
            necesita_patrocinio = necesita_raw

        if necesita_patrocinio:
            campos_requeridos = [
                'id_patrocinador',
                'carta_patrocinio',
                'prueba_relacion',
                'estados_bancarios_patrocinador',
                'prueba_ingresos',
                'detalles_empresa',
                'sponsorship_letter',
            ]
            for campo in campos_requeridos:
                if not cleaned_data.get(campo):
                    self.add_error(campo, _("Este campo es obligatorio si necesita patrocinio."))
        return cleaned_data

    def mostrar_info_patrocinio(self):
        """
        Devuelve una tupla (tiene_patrocinio, detalles) para mostrar en la plantilla.
        """
        instance = getattr(self, 'instance', None)
        if not instance or not hasattr(instance, 'tiene_patrocinio'):
            return (False, None)
        if not instance.tiene_patrocinio:
            return (False, None)
        return (True, instance.detalles_patrocinio())