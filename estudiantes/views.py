from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_countries.fields import countries
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from dashboard.views import *
from django.utils.translation import gettext as _
from django.utils.translation import activate

# Create your views here.
@login_required
@permission_required('estudiantes.view_estudiantes')
def estudiantes(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    try:
        # Obtener todos los estudiantes y contar el total
        Shinobu = Estudiantes.objects.all().order_by('id')  # Lista de estudiantes ordenada por ID descendente
        Mitsuri = Estudiantes.objects.count()  # Total de estudiantes

        # Contar documentos pendientes, aprobados y rechazados
        documentos_pendientes = DocumentosEstudiante.objects.filter(estado_inscripcion="En Revisión").count()
        documentos_aprobados = DocumentosEstudiante.objects.filter(estado_inscripcion="Aprobado").count()
        documentos_rechazados = DocumentosEstudiante.objects.filter(estado_inscripcion="Rechazado").count()

        # Paginación
        page = request.GET.get('page', 1)  # Obtener el número de página de la solicitud
        paginator = Paginator(Shinobu, 5)  # Paginador con 5 estudiantes por página

        try:
            Shinobu = paginator.page(page)  # Obtener la página solicitada
        except (EmptyPage, PageNotAnInteger):
            Shinobu = paginator.page(paginator.num_pages)  # Si la página no es válida, mostrar la última página

        # Contexto para la plantilla
        context = {
            'page_title': 'SEDA | Estudiantes',
            'Culona': Shinobu,  # Lista de estudiantes paginada
            'estudiantes': Mitsuri,  # Total de estudiantes
            'pendientes': documentos_pendientes,  # Total de documentos pendientes
            'aprobados': documentos_aprobados,  # Total de documentos aprobados
            'rechazados': documentos_rechazados,  # Total de documentos rechazados
            'paginator': paginator
        }
    except PermissionDenied:
        # Manejar el caso en que el usuario no tenga permisos
        messages.error(request, "No tienes permisos para entrar aquí")
        return redirect('E403')  # Redirigir a la página de error 403

    # Renderizar la plantilla con el contexto
    return render(request, "estudiantes.html", context)

@login_required
@permission_required('estudiantes.view_estudiantes')
def listaEstudiantes(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    query = request.GET.get('q', '').strip()

    if query:
        Gojo = Estudiantes.objects.filter(
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query) | 
            Q(pasaporte__icontains=query) | 
            Q(email__icontains=query) | 
            Q(nacionalidad__icontains=query)  # Aquí sigue filtrando por código de país
        ).order_by('fecha_creacion')
    else:
        Gojo = Estudiantes.objects.filter(is_superuser=False).order_by('fecha_creacion')

    # Convertir el código de país en nombre de país legible
    for estudiante in Gojo:
        estudiante.nacionalidad_nombre = countries.name(estudiante.nacionalidad)

    page = request.GET.get('page', 1)
    paginator = Paginator(Gojo, 5)

    try:
        Gojo = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        Gojo = paginator.page(paginator.num_pages)

    context = {
        'page_title': 'SEDA | Lista Estudiantes',
        'Gojo': Gojo,
        'paginator': paginator
    }

    return render(request, "estudiantes/estudiantes.html", context)

@login_required
@permission_required('estudiantes.add_estudiantes')
def agregarEstudiante(request): 
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    if request.method == 'POST':
        Douma = EstudiantesRegistroForm(request.POST)
        if Douma.is_valid():
            Douma.save()
            messages.success(request, "Estudiante Agregado Exitosamente!")
            return redirect('lista_estudiantes')
        else:
            messages.error(request, 'Error al intentar guardar al estudiante')
    else:
        Douma = EstudiantesRegistroForm()
        
    context = {
        'page_title': 'SEDA | Agregar Estudiante',
        'Douma': Douma
    }
    
    return render(request, "estudiantes/agregarEstudiante.html", context)

@login_required
@permission_required('estudiantes.change_estudiantes')
def actualizarEstudiante(request, id): 
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Agatsuma = get_object_or_404(Estudiantes, id=id)
    
    if request.method == 'POST':
        Zenitsu = EstudiantesActualizacionForm(request.POST, instance=Agatsuma)
        if Zenitsu.is_valid():
            Zenitsu.save()
            messages.success(request, f"{Agatsuma.nombre} {Agatsuma.apellido} actualizado Exitosamente!")
            return redirect('lista_estudiantes')
        else:
            messages.error(request, 'Error al intentar guardar al estudiante')
    else:
        Zenitsu = EstudiantesActualizacionForm(instance=Agatsuma)
        
    context = {
        'page_title': f'SEDA | {Agatsuma.nombre} {Agatsuma.apellido}',
        'Agatsuma': Zenitsu,
        'Nezuko': Agatsuma
    }
    
    return render(request, "estudiantes/actualizarEstudiante.html", context)

@login_required
@permission_required('estudiantes.delete_estudiantes')
def eliminarEstudiante(request, id): 
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Kanao = get_object_or_404(Estudiantes, id=id)
    Kanao.delete()
    messages.success(request, f"{Kanao.nombre} {Kanao.apellido} Eliminado Exitosamente")
    return redirect('lista_estudiantes')

@login_required
@permission_required('estudiantes.view_estudiantes')
def mostrarEstudiante(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    user = get_object_or_404(Estudiantes, pk=id)
    context = {
        'maki': user,
        'page_title': f'Oseed | {user.nombre} {user.apellido}',
    }

    return render(request, "estudiantes/tarjetaEstudiante.html", context)

@login_required
def subir_documentos(request):
    lang_code = request.session.get('django_language', 'en')
    activate(lang_code)

    estudiante = request.user.estudiantes
    documentos, created = DocumentosEstudiante.objects.get_or_create(estudiante=estudiante)

    if request.method == 'POST':
        form = DocumentosEstudianteForm(request.POST, request.FILES, instance=documentos)

        if form.is_valid():
            necesita_patrocinio = form.cleaned_data.get('necesita_patrocinio')

            # Validar campos obligatorios si necesita patrocinio
            if necesita_patrocinio:
                campos_patrocinio = [
                    'id_patrocinador',
                    'carta_patrocinio',
                    'prueba_relacion',
                    'estados_bancarios_patrocinador',
                    'prueba_ingresos',
                    'detalles_empresa',
                ]

                errores = []
                for campo in campos_patrocinio:
                    if not form.cleaned_data.get(campo):
                        errores.append(campo)

                if errores:
                    for campo in errores:
                        form.add_error(campo, _("Este campo es obligatorio si necesita patrocinio."))
                    messages.error(request, _("Por favor, complete todos los campos requeridos de patrocinio."))
                else:
                    form.save()
                    messages.success(request, _("Documentos subidos exitosamente."))
                    return redirect('estudiante_dashboard')
            else:
                form.save()
                messages.success(request, _("Documentos subidos exitosamente."))
                return redirect('estudiante_dashboard')
        else:
            messages.error(request, _("Por favor, corrija los errores en el formulario."))
    else:
        form = DocumentosEstudianteForm(instance=documentos)

    context = {
        'page_title': 'SEDA | Subir Documentos',
        'form': form
    }

    return render(request, 'documentos/subir_documentos.html', context)

@login_required
def actualizar_documentos(request, id):
    lang_code = request.session.get('django_language', 'en')
    activate(lang_code)

    try:
        estudiante = request.user.estudiantes
    except Estudiantes.DoesNotExist:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    documentos = get_object_or_404(DocumentosEstudiante, id=id, estudiante=estudiante)

    if request.method == 'POST':
        form = DocumentosEstudianteForm(request.POST, request.FILES, instance=documentos)

        if form.is_valid():
            necesita_patrocinio = form.cleaned_data.get('necesita_patrocinio')

            if necesita_patrocinio:
                campos_patrocinio = [
                    'id_patrocinador',
                    'carta_patrocinio',
                    'prueba_relacion',
                    'estados_bancarios_patrocinador',
                    'prueba_ingresos',
                    'detalles_empresa',
                ]

                errores = []
                for campo in campos_patrocinio:
                    if not form.cleaned_data.get(campo):
                        errores.append(campo)

                if errores:
                    for campo in errores:
                        form.add_error(campo, _("Este campo es obligatorio si necesita patrocinio."))
                    messages.error(request, _("Por favor, completa todos los campos requeridos para el patrocinio."))
                else:
                    form.save()
                    messages.success(request, _("Documentos actualizados exitosamente."))
                    return redirect('estudiante_dashboard')
            else:
                form.save()
                messages.success(request, _("Documentos actualizados exitosamente."))
                return redirect('estudiante_dashboard')
        else:
            messages.error(request, _("Por favor, corrige los errores en el formulario."))
    else:
        form = DocumentosEstudianteForm(instance=documentos)

    context = {
        'page_title': 'SEDA | Actualizar Documentos',
        'form': form
    }

    return render(request, 'documentos/actualizar_documentos.html', context)


@login_required
@permission_required('estudiantes.view_documentos_pendientes', raise_exception=True)
def documentos_pendientes(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    query = request.GET.get('q', '').strip()

    if query:
        Maki = DocumentosEstudiante.objects.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query) |
            Q(email__icontains=query) |
            Q(codigo_inscripcion__icontains=query)
        ).filter(estado_inscripcion="En Revisión").order_by('-id')
    else:
        Maki = DocumentosEstudiante.objects.filter(estado_inscripcion="En Revisión").order_by('-id')

    context = {
        'page_title': 'SEDA | Documentos Pendientes',
        'Zenin': Maki
    }

    return render(request, "pendientes/documentos_pendientes.html", context)

@login_required
@permission_required('estudiantes.view_documentos_pendientes', raise_exception=True)
def visualizarDocumentos(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Geto = get_object_or_404(DocumentosEstudiante, id=id)

    # Verificar si el estado es "Rechazado" y agregar el mensaje al contexto
    mensaje_rechazo = None
    if Geto.estado_inscripcion == "Rechazado":
        mensaje_rechazo = Geto.mensaje_rechazo

    context = {
        'page_title': f'SEDA | Documentos: {Geto.estudiante.nombre} {Geto.estudiante.apellido}',
        'Suguru': Geto,
        'mensaje_rechazo': mensaje_rechazo,  # Agregar el mensaje al contexto
    }

    return render(request, "pendientes/visualizarEstudiante.html", context)

@login_required
@permission_required('estudiantes.approve_documentos', raise_exception=True)
def documentos_aprobados(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
        
    query = request.GET.get('q', '').strip()

    if query:
        Maki = DocumentosEstudiante.objects.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query) |
            Q(email__icontains=query) | 
            Q(codigo_inscripcion__icontains=query)
        ).filter(estado_inscripcion="Aprobado").order_by('-id')
    else:
        Maki = DocumentosEstudiante.objects.filter(estado_inscripcion="Aprobado").order_by('-id')
    
    context = {
        'page_title': 'SEDA | Procesos Aprobados',
        'Zenin': Maki
    }
    
    return render(request, "pendientes/procesos_aprobados.html", context)

@login_required
@permission_required('estudiantes.reject_documentos', raise_exception=True)
def documentos_rechazados(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    query = request.GET.get('q', '').strip()

    if query:
        Maki = DocumentosEstudiante.objects.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query) |
            Q(email__icontains=query) | 
            Q(codigo_inscripcion__icontains=query)
        ).filter(estado_inscripcion="Rechazado").order_by('-id')
    else:
        Maki = DocumentosEstudiante.objects.filter(estado_inscripcion="Rechazado").order_by('-id')

    context = {
        'page_title': 'SEDA | Procesos Rechazados',
        'Zenin': Maki
    }

    return render(request, "pendientes/procesos_rechazados.html", context)

@login_required
@permission_required('estudiantes.change_documentos_estudiante')
def cambiar_estado_inscripcion(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    documentos = get_object_or_404(DocumentosEstudiante, id=id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_inscripcion')
        mensaje_rechazo = request.POST.get('mensaje_rechazo', '').strip()

        if nuevo_estado in dict(EstadoInscripcion.choices):
            documentos.estado_inscripcion = nuevo_estado

            # Si el estado es "Rechazado", guardar el mensaje de rechazo
            if nuevo_estado == EstadoInscripcion.RECHAZADO:
                if not mensaje_rechazo:
                    messages.error(request, "Debes proporcionar un motivo para el rechazo.")
                    return redirect('visualizarDocumentos', id=id)
                documentos.mensaje_rechazo = mensaje_rechazo
            else:
                documentos.mensaje_rechazo = None  # Limpiar el mensaje si no está rechazado

            documentos.save()
            messages.success(request, f"El estado de inscripción se cambió a {nuevo_estado}.")
        else:
            messages.error(request, "Estado de inscripción no válido.")

    return redirect('estudiantes')

@login_required
def actualizar_perfil_estudiante(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    # Obtener el usuario autenticado como instancia de Estudiantes
    estudiante = get_object_or_404(Estudiantes, id=request.user.id)

    if request.method == 'POST':
        form = EstudiantesActualizacionForm(request.POST, request.FILES, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('estudiante_dashboard')  # Redirigir al dashboard o a otra página
        else:
            messages.error(request, "Hubo un error al actualizar el perfil.")
    else:
        form = EstudiantesActualizacionForm(instance=estudiante)

    context = {
        'page_title': f'SEDA | Actualizar Perfil',
        'form': form,
        'user': estudiante
    }

    return render(request, 'estudiantes/actualizarPerfil.html', context)

@login_required
@permission_required('estudiantes.reject_documentos', raise_exception=True)
def eliminarRegistros(request, id):
    Mai = get_object_or_404(DocumentosEstudiante, id=id)
    Mai.delete()
    messages.success(request, f"Documentos de {Mai.estudiante.nombre} {Mai.estudiante.apellido} eliminados exitosamente.")
    return redirect('estudiantes')