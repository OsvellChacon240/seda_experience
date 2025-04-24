class DebugLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Sesión habilitada: {'session' in dir(request)}")
        print(f"Idioma desde la sesión: {request.session.get('django_language', 'No configurado')}")
        print(f"Idioma actual antes del middleware: {getattr(request, 'LANGUAGE_CODE', 'No configurado')}")
        response = self.get_response(request)
        print(f"Idioma actual después del middleware: {getattr(request, 'LANGUAGE_CODE', 'No configurado')}")
        return response