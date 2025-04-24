from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from auditlog.models import LogEntry
from usuarios.models import CustomUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from dashboard.views import *

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/')  # Redirigir si no es superusuario
def auditoria(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    logs_list = LogEntry.objects.all().order_by('-timestamp')
    page = request.GET.get('page', 1)
    paginator = Paginator(logs_list, 6)

    try:
        entity = paginator.page(page)
    except PageNotAnInteger:
        entity = paginator.page(1)
    except EmptyPage:
        entity = paginator.page(paginator.num_pages)
    
    # Obtener el nombre del usuario logueado
    if request.user.is_authenticated:
        nombre_usuario = request.user.get_full_name()
    else:
        nombre_usuario = None

    return render(request, 'auditoria.html', {
        'logs': entity,
        'paginator': paginator,
        'entity': entity,
        'nombre_usuario': nombre_usuario,  # Pasar el nombre de usuario al contexto
        'page_title': 'SEDA | Auditoria'
    })