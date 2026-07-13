from django.core.cache import cache

from .models import Lideranca, Voluntario


def leads_pendentes(request):
    """Contagens de cadastros do app aguardando aprovação, para os badges do menu —
    leads (Lideranças) e voluntários (Equipes), só p/ quem tem permissão de aprovar.

    Roda em TODA página HTML; os dois COUNT são cacheados por ~60s (o badge tolera
    esse atraso), para não onerar cada request — especialmente com o Postgres remoto.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}
    ctx = {}
    try:
        if user.pode_acessar('liderancas:aprovar'):
            ctx['leads_pendentes_count'] = cache.get_or_set(
                'badge_leads_pendentes',
                lambda: Lideranca.objects.filter(aprovacao='pendente').count(),
                60,
            )
        if user.pode_acessar('equipes:aprovar'):
            ctx['voluntarios_pendentes_count'] = cache.get_or_set(
                'badge_voluntarios_pendentes',
                lambda: Voluntario.objects.filter(aprovacao='pendente').count(),
                60,
            )
    except Exception:
        return {}
    return ctx
