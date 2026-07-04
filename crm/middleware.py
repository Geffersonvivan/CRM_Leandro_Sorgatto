from django.shortcuts import redirect

VINCULOS_PWA = {'coordenador', 'cabo', 'replicador'}

# Prefixos que usuários PWA podem acessar
PREFIXOS_PWA = ('/app/', '/login/', '/logout/', '/static/', '/media/', '/admin/')


class RedirecionarUsuarioPWA:
    """
    Usuários com vínculo PWA (coordenador, cabo, replicador)
    são redirecionados para o app móvel ao tentar acessar o CRM desktop.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and hasattr(request.user, 'vinculo')
            and request.user.vinculo in VINCULOS_PWA
            and not any(request.path.startswith(p) for p in PREFIXOS_PWA)
        ):
            return redirect('pwa:dashboard')

        return self.get_response(request)
