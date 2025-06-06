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
from django.utils.translation import gettext_lazy as _

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
            messages.success(request, _("Employee Successfully Added!"))
            return redirect('empleados')
        else:
            messages.error(request, _("There was an error adding the employee."))
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
        messages.error(request, _('To update your own user you can do it from "Settings".'))
        return redirect('empleados')
    
    if Konan.id == 1:
        messages.error(request, "You cannot update the administrator user.")
        return redirect('empleados')
    
    if request.method == 'POST':
        Mikasa = actEmpleadosFrm(request.POST, request.FILES, instance=Konan)
        if Mikasa.is_valid():
            Mikasa.save()
            messages.success(
                request,
                _("We have successfully updated to: %(nombre)s %(apellido)s") % {
                    "nombre": Konan.nombre,
                    "apellido": Konan.apellido
                }
            )
            return redirect('empleados')
        else:
            messages.error(request, _("There was an error updating the employee."))
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
        messages.error(request, _("You can't delete your own user."))
        return redirect('empleados')
    
    if Maki.id == 1:
        messages.error(request, _("You cannot delete the administrator user."))
        return redirect('empleados')
    
    Maki.delete()
    messages.success(request, _(f"{Maki.nombre} {Maki.apellido} no longer belongs to the system"))
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
        messages.success(request, _("Permits updated correctly."))
        return redirect('viewUser', id=user_id)
    
    messages.error(request, _("Request method not allowed."))
    return redirect('viewUser', id=user_id)

@login_required
@permission_required('auth.delete_permission')
def quitar_permiso(request, user_id, permission_id):
    user = get_object_or_404(Empleado, pk=user_id)
    permission = get_object_or_404(Permission, pk=permission_id)
    
    try:
        user.user_permissions.remove(permission)
        messages.success(request, _("Permit successfully removed."))
    except Permission.DoesNotExist:
        messages.error(request, _("The selected permit does not exist."))
    except Empleado.DoesNotExist:
        messages.error(request, _("The selected user does not exist."))

    return redirect('viewUser', id=user_id)

@login_required
@permission_required('usuarios.view_customuser')
def tarjetaUsuarios(request, id):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    user = get_object_or_404(Empleado, pk=id)

    if user.id == 1 and request.user.id != 1:
        messages.error(request, _("You are not allowed to view administrator information."))
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
        messages.success(request, _("Permits updated correctly."))
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
            messages.success(request, _('Position successfully created!'))
            return redirect('cargos')
        else:
            messages.error(request, _('There was an error in adding the charge.'))
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
        messages.error(request, _("You cannot update the administrator position."))
        return redirect('cargos')
    
    if request.method == 'POST':
        Bardock = CargosFrm(request.POST, instance=Granola)
        if Bardock.is_valid():
            Bardock.save()
            messages.success(request, "Position Successfully Updated!")
            return redirect('cargos')
        else:
            messages.error(request, _("There was an error updating the charge."))
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
        messages.error(request, _("You cannot delete the administrator position."))
        return redirect('cargos')
    
    # Obtener el empleado relacionado con el usuario autenticado
    try:
        empleado = Empleado.objects.get(id=request.user.id)
    except Empleado.DoesNotExist:
        empleado = None

    if empleado and empleado.cargo == Jogo:
        messages.error(request, _("You cannot delete the charge that is assigned to your user."))
        return redirect('cargos')
    
    Jogo.delete()
    messages.success(request, _("Charge Successfully Removed"))
    return redirect('cargos')

@login_required
def actualizar_perfil_empleado(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    try:
        # Verificar si el usuario autenticado es una instancia de Empleado
        empleado = Empleado.objects.get(id=request.user.id)
    except Empleado.DoesNotExist:
        raise Http404(_("No employee profile associated with this user was found.."))

    if request.method == 'POST':
        form = actEmpleadosFrm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated correctly."))
            return redirect('dashboard')  # Redirigir al dashboard
        else:
            messages.error(request, _("Error updating the profile. Please correct the errors."))
    else:
        form = actEmpleadosFrm(instance=empleado)

    context = {
        'page_title': f'SEDA | Actualizar Perfil',
        'form': form,
        'user': empleado
    }

    return render(request, 'empleados/actualizarPerfil.html', context)