from django.shortcuts import render, redirect
from usuarios.models import Empleado
from estudiantes.models import Estudiantes, DocumentosEstudiante
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from estudiantes.models import DocumentosEstudiante
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import activate
from django.conf import settings
from django.utils.translation import get_language

# Create your views here.

def change_language(request, lang_code):
    if lang_code in dict(settings.LANGUAGES):
        activate(lang_code)
        request.session['django_language'] = lang_code  # Guarda el idioma en la sesión
        print(f"Idioma cambiado a: {lang_code}")  # Depuración
    else:
        print(f"Idioma no válido: {lang_code}")  # Depuración
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def dashboard(request):
    # Forzar el idioma desde la sesión
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    print(f"Idioma actual en la vista después de activar: {get_language()}")  # Depuración

    # Contar usuarios y estudiantes
    Megumi = Empleado.objects.count()
    Itadori = Estudiantes.objects.count()

    # Contar documentos pendientes, aprobados y rechazados
    documentos_pendientes = DocumentosEstudiante.objects.filter(estado_inscripcion="En Revisión").count()
    documentos_aprobados = DocumentosEstudiante.objects.filter(estado_inscripcion="Aprobado").count()
    documentos_rechazados = DocumentosEstudiante.objects.filter(estado_inscripcion="Rechazado").count()

    # Obtener los documentos pendientes para mostrarlos en el dashboard
    documentos_pendientes_lista = DocumentosEstudiante.objects.filter(estado_inscripcion="En Revisión").order_by('-fecha_subida')[:5]  # Mostrar los 5 más recientes

    # Paginación de estudiantes
    Maki = Estudiantes.objects.all().order_by('-id')  # Ordenar por el campo 'id'
    page = request.GET.get('page', 1)
    paginator = Paginator(Maki, 5)

    try:
        Maki = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        Maki = paginator.page(paginator.num_pages)

    # Contexto para la plantilla
    context = {
        'page_title': 'SEDA | Dashboard',
        'usuarios': Megumi,  # Total de empleados
        'estudiantes': Itadori,  # Total de estudiantes
        'Zenin': Maki,  # Lista de estudiantes paginada
        'paginator': paginator,  # Paginador
        'pendientes': documentos_pendientes,  # Total de documentos pendientes
        'aprobados': documentos_aprobados,  # Total de documentos aprobados
        'rechazados': documentos_rechazados,  # Total de documentos rechazados
        'documentos_pendientes_lista': documentos_pendientes_lista,  # Lista de documentos pendientes
    }

    return render(request, "dashboard.html", context)

@login_required
def buscar(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    query = request.GET.get('q', '').strip()
    if not query:
        messages.error(request, 'Por favor, introduce un criterio de búsqueda.')
        return redirect('dashboard')

    # Buscar en Empleados
    try:
        user = Empleado.objects.get(username=query)
        return redirect('viewUser', id=user.id)  # Cambiar 'user_id' por 'id'
    except Empleado.DoesNotExist:
        pass

    try:
        user = Empleado.objects.get(nombre__icontains=query)
        return redirect('viewUser', id=user.id)  # Cambiar 'user_id' por 'id'
    except Empleado.DoesNotExist:
        pass

    try:
        user = Empleado.objects.get(pasaporte=query)
        return redirect('viewUser', id=user.id)  # Cambiar 'user_id' por 'id'
    except Empleado.DoesNotExist:
        pass
    
    try:
        user = Empleado.objects.get(email__icontains=query)
        return redirect('viewUser', id=user.id)  # Cambiar 'user_id' por 'id'
    except Empleado.DoesNotExist:
        pass

    # Buscar en Estudiantes
    try:
        estudiante = Estudiantes.objects.get(nombre__icontains=query)
        return redirect('verEstudiante', id=estudiante.id)
    except Estudiantes.DoesNotExist:
        pass

    try:
        estudiante = Estudiantes.objects.get(pasaporte__icontains=query)
        return redirect('verEstudiante', id=estudiante.id)
    except Estudiantes.DoesNotExist:
        pass
    
    try:
        estudiante = Estudiantes.objects.get(pasaporte__icontains=query)
        return redirect('verEstudiante', id=estudiante.id)
    except Estudiantes.DoesNotExist:
        pass

    # Buscar en Documentos
    documento = DocumentosEstudiante.objects.filter(codigo_inscripcion__icontains=query)
    if documento.exists():
        return redirect('visualizarDocumento', id=documento.first().id)

    return redirect('E404')

@login_required
def error404(request): 
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    context = {
        'page_title': 'SEDA | No se encontro la informacion'
    }
    
    return render(request, "error-404.html", context)

def error403(request): 
    
    context = {
        'page_title': 'SEDA | No tienes permisos para estar aqui'
    }
    
    return render(request, "error-403.html", context)

@login_required
def estudiante_dashboard(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    # Obtener los documentos del estudiante logueado
    documentos = DocumentosEstudiante.objects.filter(estudiante=request.user).first()

    # Calcular el progreso de los documentos subidos
    progreso = documentos.calcular_progreso() if documentos else 0

    # Paginación de los documentos (si es necesario)
    Maki = [documentos] if documentos else []  # Convertir a lista para paginar
    page = request.GET.get('page', 1)
    paginator = Paginator(Maki, 5)

    try:
        Maki = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        Maki = paginator.page(paginator.num_pages)

    context = {
        'page_title': 'SEDA | Dashboard - Estudiantes',
        'Zenin': Maki,  # Paginador de documentos
        'progreso': progreso,  # Progreso de los documentos subidos
        'paginator': paginator,
        'documentos': documentos,  # Pasamos los documentos al contexto
    }

    return render(request, "dashboardEstudiantes.html", context)
