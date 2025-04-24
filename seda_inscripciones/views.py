from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import logout
from django.contrib.auth.models import User
from usuarios.models import *
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from usuarios.models import CustomUser
from estudiantes.forms import EstudiantesRegistroForm
from django.contrib import messages
from django.utils.translation import activate
from django.conf import settings
from dashboard.views import *

def login_view(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'en'
    activate(lang_code)
    
    login_error = False
    inactive_error = False
    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username_or_email = request.POST.get('username_or_email') 
        password = request.POST.get('password') 

        user = CustomUser.objects.filter(username=username_or_email).first() or CustomUser.objects.filter(email=username_or_email).first()

        if user:
            if not user.status:
                inactive_error = True
            else:
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)

                    # Verificar si el usuario es un estudiante o un empleado
                    if hasattr(user, 'estudiantes') and user.estudiantes.rol:  
                        return redirect('estudiante_dashboard')
                    else:
                        return redirect('dashboard')  # Redirige al dashboard del empleado
                else:
                    login_error = True
        else:
            login_error = True

    return render(request, 'registration/login.html', {
        'form': form,
        'login_error': login_error,
        'inactive_error': inactive_error,
        'page_title': 'SEDA | Login'
    })

    
def registrar_estudiante(request):
    
    lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
    activate(lang_code)
    
    if request.method == "POST":
        form = EstudiantesRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Estudiante Registrado Exitosamente, Intenta Iniciar Sesion")
            return redirect('login')  # Redirige al login tras el registro
    else:
        form = EstudiantesRegistroForm()
        
    context = {
        'page_title': 'SEDA | Registro',
        'form': form
    }
    
    return render(request, 'registration/register.html', context)

def cerrar_sesion(request):
    logout(request)
    return redirect('login')