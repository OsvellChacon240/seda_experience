from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from PIL import Image
import re
from auditlog.registry import auditlog
from datetime import date
from django.utils.timezone import now

# Modelo para los cargos
class Cargo(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# Opciones para género
class GeneroChoices(models.TextChoices):
    MASCULINO = 'M', _('Masculino')
    FEMENINO = 'F', _('Femenino')

# Validaciones
# ... (Mantenemos las mismas funciones de validación)

def validar_nombre(value):
    regex = r"^[a-zA-ZñÑáéíóúÁÉÍÓÚ ]+$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El nombre no tiene el formato correcto. Asegúrate de usar solo letras y espacios.")

def validar_fecha_nacimiento(value):
    if value > date.today():
        raise ValidationError("La fecha de nacimiento no puede ser futura.")

def validar_foto_perfil(value):
    try:
        img = Image.open(value)
        if img.format not in ['JPEG', 'PNG']:
            raise ValidationError("La imagen debe ser en formato JPEG o PNG.")
    except IOError:
        raise ValidationError("El archivo no es una imagen válida.")

def validar_pasaporte(value):
    """
    Valida que el pasaporte tenga un formato alfanumérico válido.
    Ejemplo: Debe contener entre 6 y 9 caracteres alfanuméricos.
    """
    regex = r"^[a-zA-Z0-9]{6,9}$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El pasaporte debe contener entre 6 y 9 caracteres alfanuméricos.")
    
# Modelo base abstracto
class CustomUser(AbstractUser):
    nombre = models.CharField(max_length=50, validators=[validar_nombre], blank=True)
    apellido = models.CharField(max_length=50, validators=[validar_nombre], blank=True)
    pasaporte = models.CharField(
        max_length=9,
        unique=True,
        verbose_name=_('Pasaporte'),
        validators=[validar_pasaporte],
        blank=True
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('Teléfono'),
    )
    genero = models.CharField(
            max_length=1,
            choices=GeneroChoices.choices,
            default=GeneroChoices.MASCULINO,
            verbose_name=_('Género'),
            blank=True
        )
    direccion = models.TextField(blank=True, null=True, verbose_name=_('Dirección'))
    fecha_nacimiento = models.DateField(
        verbose_name=_('Fecha de nacimiento'),
        validators=[validar_fecha_nacimiento],
        null=True,
        blank=True
    )
    foto_perfil = models.ImageField(
        upload_to='usuarios/',
        default='perfil/default.jpg',
        validators=[validar_foto_perfil],
        blank=True
    )

    status = models.BooleanField(default=True, verbose_name=_('Estado de Cuenta'))

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def edad(self):
        if self.fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - self.fecha_nacimiento.year
            if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                edad -= 1
            return edad
        return None

    @property
    def dias_para_cumple(self):
        if self.fecha_nacimiento:
            hoy = date.today()
            proximo_cumple = self.fecha_nacimiento.replace(year=hoy.year)
            if proximo_cumple < hoy:
                proximo_cumple = proximo_cumple.replace(year=hoy.year + 1)
            return (proximo_cumple - hoy).days
        return None

    @property
    def tiempo_desde_registro(self):
        if self.fecha_creacion:
            return (now() - self.fecha_creacion).days
        return None

    def save(self, *args, **kwargs):
        if not self.username:  # Si no se proporciona un username
            self.username = f"{self.email.split('@')[0]}_{self.pasaporte}"  # Generar un username único basado en el email y pasaporte
        super().save(*args, **kwargs)

# Modelo de Empleado
class Empleado(CustomUser):
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, verbose_name=_('Cargo'), null=True, blank=True)

    def __str__(self):
        return f"Empleado: {self.nombre} {self.apellido} ({self.pasaporte})"
    
auditlog.register(Empleado)