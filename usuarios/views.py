from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from auditlog.models import LogEntry
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import Http404
from dashboard.views import *

# Create your views here.

@login_required
@permission_required('usuarios.view_customuser')
def usuarios(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Makima = Empleado.objects.all().order_by('-id')
    Power = Empleado.objects.count()
    Nobara = Cargo.objects.count()
    
    page = request.GET.get('page', 1)

    paginator = Paginator(Makima, 5)

    try:
        Makima = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        Makima = paginator.page(paginator.num_pages)
    
    
    context = {
        'page_title': 'SEDA | Usuarios',
        'Culona': Makima,
        'power': Power,
        'nobara': Nobara,
        'paginator': paginator
    }
    
    return render(request, "usuarios.html", context)

@login_required
@permission_required('usuarios.view_customuser')
def mostrarUsuarios(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    # Obtener el término de búsqueda desde la query string (GET)
    query = request.GET.get('q', '').strip()

    # Filtrar los usuarios si se proporciona una búsqueda
    if query:
        Denji = Empleado.objects.filter(
            is_superuser=False
        ).filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query) | Q(pasaporte__icontains=query) | Q(email__icontains=query)
        ).order_by('pasaporte')
    else:
        # Si no se pasa un término de búsqueda, se muestran todos
        Denji = Empleado.objects.filter(is_superuser=False).order_by('pasaporte')

    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(Denji, 5)

    try:
        Denji = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        Denji = paginator.page(paginator.num_pages)

    context = {
        'page_title': 'SEDA | Empleados',
        'paginator': paginator,
        'Reze': Denji,
        'query': query  # Pasar el término de búsqueda a la plantilla
    }

    return render(request, "empleados/verEmpleados.html", context)

@login_required
@permission_required('usuarios.add_customuser')
def addUsuarios(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    if request.method == 'POST':
        Shinobu = EmpleadosFrm(request.POST, request.FILES)
        if Shinobu.is_valid():
            Shinobu.save()
            messages.success(request, "Empleado Agregado Exitosamente!")
            return redirect('empleados')
        else:
            messages.error(request, "Hubo un error al agregar al empleado.")
    else:
        Shinobu = EmpleadosFrm()

    context = {
        'page_title': 'SEDA | Agregar Usuarios',
        'Shinobu': Shinobu
    }
    return render(request, "empleados/addEmpleados.html", context)

@login_required
@permission_required('usuarios.change_customuser')
def actUsuarios(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Konan = get_object_or_404(Empleado, id=id)
    
    if Konan == request.user:
        messages.error(request, 'Para actualizar tu propio usuario puedes hacerlo desde "Configuraciones"')
        return redirect('empleados')
    
    if Konan.id == 1:
        messages.error(request, "No puedes actualizar al usuario administrador.")
        return redirect('empleados')
    
    if request.method == 'POST':
        Mikasa = actEmpleadosFrm(request.POST, request.FILES, instance=Konan)
        if Mikasa.is_valid():
            Mikasa.save()
            messages.success(request, f'Hemos Actualizado Con Exito A: {Konan.nombre} {Konan.apellido}')
            return redirect('empleados')
        else:
            messages.error(request, "Hubo un error al actualizar al empleado.")
    else:
        Mikasa = actEmpleadosFrm(instance=Konan)
        
    context = {
        'page_title': f'SEDA | {Konan.nombre} {Konan.apellido}',
        'Mikasa': Mikasa,
        'Konan': Konan
    }
        
    return render(request, 'empleados/actEmpleados.html', context)

@login_required
@permission_required('app.delete_customuser')
def dltUsuarios(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Maki = get_object_or_404(Empleado, id=id)
    
    if Maki == request.user:
        messages.error(request, "¿Eres tonto?, No puedes eliminar tu propio usuario.")
        return redirect('empleados')
    
    if Maki.id == 1:
        messages.error(request, "No puedes eliminar al usuario administrador.")
        return redirect('empleados')
    
    Maki.delete()
    messages.success(request, f"{Maki.nombre} {Maki.apellido} ya no pertenece al sistema")
    return redirect('empleados')

@login_required
@permission_required('auth.view_permission')
def view_user_permissions(request, user_id):
    user = Empleado.objects.get(pk=user_id)
    permissions = user.user_permissions.all()  # Obtener los permisos del usuario
    return render(request, 'user_permissions_view.html', {'user': user, 'permissions': permissions})

@login_required
@permission_required('auth.add_permission')
def asignar_permiso(request, user_id, permission_id):
    user = get_object_or_404(Empleado, pk=user_id)
    permission = get_object_or_404(Permission, pk=permission_id)

    if request.method == 'POST':
        permisos_seleccionados = request.POST.getlist('permisos')
        user.user_permissions.set(permisos_seleccionados)
        messages.success(request, "Permisos actualizados correctamente.")
        return redirect('viewUser', id=user_id)
    
    messages.error(request, "Método de solicitud no permitido.")
    return redirect('viewUser', id=user_id)

@login_required
@permission_required('auth.delete_permission')
def quitar_permiso(request, user_id, permission_id):
    user = get_object_or_404(Empleado, pk=user_id)
    permission = get_object_or_404(Permission, pk=permission_id)
    
    try:
        user.user_permissions.remove(permission)
        messages.success(request, "Permiso quitado correctamente.")
    except Permission.DoesNotExist:
        messages.error(request, "El permiso seleccionado no existe.")
    except Empleado.DoesNotExist:
        messages.error(request, "El usuario seleccionado no existe.")

    return redirect('viewUser', id=user_id)

@login_required
@permission_required('usuarios.view_customuser')
def tarjetaUsuarios(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    user = get_object_or_404(Empleado, pk=id)

    if user.id == 1 and request.user.id != 1:
        messages.error(request, "No tienes permitido ver la información del administrador.")
        return redirect('empleados')

    user_action_logs = LogEntry.objects.filter(actor_id=id)[:3]

    paginator = Paginator(user_action_logs, 2)
    page = request.GET.get('page')
    try:
        user_action_logs = paginator.page(page)
    except PageNotAnInteger:
        user_action_logs = paginator.page(1)
    except EmptyPage:
        user_action_logs = paginator.page(paginator.num_pages)

    all_permissions = Permission.objects.all()  # Todos los permisos disponibles
    user_permissions = user.user_permissions.all()  # Permisos actuales del usuario
    user_permissions_count = user_permissions.count()
    permission_id = 1 if Permission.objects.filter(pk=1).exists() else None

    if request.method == 'POST':
        permisos_seleccionados = request.POST.getlist('permisos')
        user.user_permissions.set(permisos_seleccionados)  # Actualizar permisos
        messages.success(request, "Permisos actualizados correctamente.")
        return redirect('empleados')

    context = {
        'maki': user,
        'user_action_logs': user_action_logs,
        'all_permissions': all_permissions,
        'user_permissions': user_permissions,
        'user_permissions_count': user_permissions_count,
        'permission_id': permission_id,
        'page_title': f'Oseed | {user.nombre} {user.apellido}',
        'paginator': paginator,
    }

    return render(request, "empleados/tarjetaEmpleado.html", context)

def cuenta_bloqueada(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    return render(request, 'cuenta_bloqueada.html')

#Backend para cargos
@login_required
@permission_required('usuarios.view_cargo')
def Cargos(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Goku = Cargo.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        Vegeta = CargosFrm(request.POST)
        if Vegeta.is_valid():
            Vegeta.save()
            messages.success(request, "Cargo Registrado Con Exito")
            return redirect('cargos')
        else:
            messages.error(request, 'Hubo un problema al cargar el Cargo')
    else:
        Vegeta = CargosFrm()
        
    page = request.GET.get('page', 1)

    paginator = Paginator(Goku, 5)

    try:
        Goku = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        Goku = paginator.page(paginator.num_pages)
    
        
    context = {
        'page_title': 'SEDA | Agregar Cargos',
        'Vegeta': Vegeta,
        'Goku': Goku,
        'paginator': paginator
    }
    
    return render(request, "cargos/cargos.html", context)

@login_required
@permission_required('usuarios.change_cargo')
def actCargos(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Granola = get_object_or_404(Cargo, id=id)
    
    if Granola.nombre == 'Administrador':
        messages.error(request, "Olvidalo no puedes cambiar al admin por este medio")
        return redirect('cargos')
    
    if request.method == 'POST':
        Bardock = CargosFrm(request.POST, instance=Granola)
        if Bardock.is_valid():
            Bardock.save()
            messages.success(request, "Cargo Actualizado Con Exito!")
            return redirect('cargos')
        else:
            messages.error(request, "Hubo un problema al actualizar el cargo")
    else:
        Bardock = CargosFrm(instance=Granola)
        
    context = {
        'page_title': f'SEDA | {Granola.nombre}',
        'Bardock': Bardock,
        'Granola': Granola
    }
    
    return render(request, 'cargos/actCargos.html', context)


@login_required
@permission_required('usuarios.delete_cargo')
def dltCargos(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    Jogo = get_object_or_404(Cargo, id=id)
    
    if Jogo.nombre == 'Administrador':
        messages.error(request, "¿Enserio? Tampoco puedes eliminar al admin por este medio")
        return redirect('cargos')
    
    if request.user.cargo == Jogo:
        messages.error(request, "No puedes eliminar tu propio cargo.")
        return redirect('cargos')
    
    Jogo.delete()
    messages.success(request, "Cargo Eliminado Con Exito")
    return redirect('cargos')

@login_required
def actualizar_perfil_empleado(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    try:
        # Verificar si el usuario autenticado es una instancia de Empleado
        empleado = Empleado.objects.get(id=request.user.id)
    except Empleado.DoesNotExist:
        raise Http404("No se encontró un perfil de empleado asociado con este usuario.")

    if request.method == 'POST':
        form = actEmpleadosFrm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('dashboard')  # Redirigir al dashboard
        else:
            messages.error(request, "Hubo un error al actualizar el perfil.")
    else:
        form = actEmpleadosFrm(instance=empleado)

    context = {
        'page_title': f'SEDA | Actualizar Perfil',
        'form': form,
        'user': empleado
    }

    return render(request, 'empleados/actualizarPerfil.html', context)