from django.utils.translation import activate
    
class ActivateLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Obtén el idioma de la sesión y actívalo
        lang_code = request.session.get('django_language', 'en')  # Idioma por defecto: 'es'
        activate(lang_code)
        return self.get_response(request)