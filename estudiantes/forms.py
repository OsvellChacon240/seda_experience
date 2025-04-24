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
            raise ValidationError("La fecha de nacimiento es obligatoria.")
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad < 16:
            raise ValidationError("El estudiante debe tener al menos 16 años.")
        return fecha_nacimiento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
    
    # Validación personalizada para el pasaporte
    def clean_pasaporte(self):
        pasaporte = self.cleaned_data.get('pasaporte')
        if Estudiantes.objects.filter(pasaporte=pasaporte).exists():
            raise ValidationError("Ya existe un estudiante con este pasaporte.")
        return pasaporte

    # Validación personalizada para el teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validar formato internacional con prefijo de país, sin espacios, guiones o paréntesis
            if not re.match(r'^\+\d{1,4}\d{7,15}$', telefono):
                raise ValidationError(
                    "El número de teléfono debe estar en formato internacional, comenzando con '+' seguido del prefijo del país y el número, sin espacios, guiones o paréntesis. Ejemplo: +584147080725 o +14155552671."
                )
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
            raise ValidationError("Ya existe un estudiante con este pasaporte.")
        return pasaporte

    # Validación personalizada para el teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validar formato internacional con prefijo de país, sin espacios, guiones o paréntesis
            if not re.match(r'^\+\d{1,4}\d{7,15}$', telefono):
                raise ValidationError(
                    "El número de teléfono debe estar en formato internacional, comenzando con '+' seguido del prefijo del país y el número, sin espacios, guiones o paréntesis. Ejemplo: +584147080725 o +14155552671."
                )
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
            'pasaporte', 'documento_identidad', 'antecedentes_penales', 'seguro_medico',
            'carta_inscripcion', 'recibo_pago', 'diploma_traducido', 'transcripcion_traducida',
            'carta_intencion', 'resumen_financiero', 'extracto_bancario',
            'necesita_patrocinio', 'id_patrocinador', 'carta_patrocinio', 'prueba_relacion',
            'estados_bancarios_patrocinador', 'prueba_ingresos', 'detalles_empresa',
        ]

        widgets = {
            field: forms.ClearableFileInput(attrs={'class': 'form-control file-input'})
            for field in [
                'pasaporte', 'documento_identidad', 'antecedentes_penales', 'seguro_medico',
                'carta_inscripcion', 'recibo_pago', 'diploma_traducido', 'transcripcion_traducida',
                'carta_intencion', 'resumen_financiero', 'extracto_bancario',
                'id_patrocinador', 'carta_patrocinio', 'prueba_relacion',
                'estados_bancarios_patrocinador', 'prueba_ingresos', 'detalles_empresa',
            ]
        }

        # Usamos un select en lugar de un checkbox para el campo de patrocinio
        widgets['necesita_patrocinio'] = forms.Select(choices=[
            (True, _('Sí')),
            (False, _('No')),
        ], attrs={'class': 'form-control'})

        labels = {
            'pasaporte': _("Pasaporte"),
            'documento_identidad': _("Documento de Identidad"),
            'antecedentes_penales': _("Antecedentes Penales"),
            'seguro_medico': _("Seguro Médico"),
            'carta_inscripcion': _("Carta de Inscripción"),
            'recibo_pago': _("Recibo de Pago"),
            'diploma_traducido': _("Diploma Traducido"),
            'transcripcion_traducida': _("Transcripción Traducida"),
            'carta_intencion': _("Carta de Intención"),
            'resumen_financiero': _("Resumen Financiero"),
            'extracto_bancario': _("Extracto Bancario"),
            'necesita_patrocinio': _("¿Necesita patrocinio?"),
            'id_patrocinador': _("ID o Pasaporte del Patrocinador"),
            'carta_patrocinio': _("Carta de Patrocinio"),
            'prueba_relacion': _("Prueba de Relación"),
            'estados_bancarios_patrocinador': _("Estado Bancario del Patrocinador (6 meses)"),
            'prueba_ingresos': _("Prueba de Ingresos del Patrocinador"),
            'detalles_empresa': _("Documentos de Empresa del Patrocinador"),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            file_fields = [
                'pasaporte', 'documento_identidad', 'antecedentes_penales', 'seguro_medico',
                'carta_inscripcion', 'recibo_pago', 'diploma_traducido', 'transcripcion_traducida',
                'carta_intencion', 'resumen_financiero', 'extracto_bancario',
                'id_patrocinador', 'carta_patrocinio', 'prueba_relacion',
                'estados_bancarios_patrocinador', 'prueba_ingresos', 'detalles_empresa',
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
            ]
            for campo in campos_requeridos:
                if not cleaned_data.get(campo):
                    self.add_error(campo, _("Este campo es obligatorio si necesita patrocinio."))
        return cleaned_data