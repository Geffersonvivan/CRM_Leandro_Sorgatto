from .models import Lideranca, Voluntario


def leads_pendentes(request):
    """Contagens de cadastros do app aguardando aprovação, para os badges do menu —
    leads (Lideranças) e voluntários (Equipes), só p/ quem tem permissão de aprovar."""
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}
    ctx = {}
    try:
        if user.pode_acessar('liderancas:aprovar'):
            ctx['leads_pendentes_count'] = Lideranca.objects.filter(aprovacao='pendente').count()
        if user.pode_acessar('equipes:aprovar'):
            ctx['voluntarios_pendentes_count'] = Voluntario.objects.filter(aprovacao='pendente').count()
    except Exception:
        return {}
    return ctx
