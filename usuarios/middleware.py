from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

class BlockInactiveUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs relevantes
        bloqueada_url = reverse('cuenta_bloqueada')  # Página de cuenta bloqueada
        login_url = reverse('login')  # Página de inicio de sesión

        if request.user.is_authenticated:
            # Verifica si el usuario está bloqueado
            if not request.user.status:
                # Si el usuario no está ya en la página de cuenta bloqueada o login
                if request.path not in [bloqueada_url, login_url]:
                    logout(request)  # Cierra la sesión del usuario
                    return redirect('cuenta_bloqueada')  # Redirige a la página de notificación
        return self.get_response(request)
