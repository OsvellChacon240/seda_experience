from django.contrib import admin
from .models import Estudiantes, DocumentosEstudiante

@admin.register(Estudiantes)
class EstudiantesAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'nacionalidad')  # Mostramos la nacionalidad

admin.site.register(DocumentosEstudiante)