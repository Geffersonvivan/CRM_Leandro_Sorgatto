from django.conf import settings


def campanha(request):
    """Expõe a identidade da campanha (settings.CAMPANHA) a todos os templates como
    {{ campanha.candidato_nome }}, {{ campanha.partido_sigla }}, etc. Fonte única de
    branding — evita nome/partido/número hardcodados espalhados pelos templates."""
    c = settings.CAMPANHA
    return {
        'campanha': {
            'candidato_nome': c['CANDIDATO_NOME'],
            'candidato_primeiro_nome': c['CANDIDATO_PRIMEIRO_NOME'],
            'partido_sigla': c['PARTIDO_SIGLA'],
            'partido_numero': c['PARTIDO_NUMERO'],
            'cargo_2026': c['CARGO_2026'],
            'tse_cargo_2026': c['TSE_CARGO_2026'],
            'uf': c['UF'],
            'cores': c['CORES'],
        }
    }
