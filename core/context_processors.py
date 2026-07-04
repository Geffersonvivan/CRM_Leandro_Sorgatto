from django.conf import settings


def campanha(request):
    """Expõe a identidade da campanha (settings.CAMPANHA) a todos os templates como
    {{ campanha.candidato_nome }}, {{ campanha.partido_sigla }}, etc. Fonte única de
    branding — evita nome/partido/número hardcodados espalhados pelos templates."""
    c = settings.CAMPANHA
    nome = c['CANDIDATO_PRIMEIRO_NOME']
    art = c.get('CANDIDATO_ARTIGO', 'a')
    return {
        'campanha': {
            'candidato_nome': c['CANDIDATO_NOME'],
            'candidato_primeiro_nome': nome,
            # Formas prontas para texto corrido, com o artigo da config —
            # "a Isadora" / "o Sorgatto" sem quebrar a gramática entre marcas.
            'trat_nome': f'{art} {nome}',                              # "a Isadora"
            'de_nome': f'd{art} {nome}',                               # "da Isadora"
            'em_nome': f'n{art} {nome}',                               # "na Isadora"
            'a_nome': f'à {nome}' if art == 'a' else f'ao {nome}',     # "à Isadora"
            'partido_sigla': c['PARTIDO_SIGLA'],
            'partido_numero': c['PARTIDO_NUMERO'],
            'cargo_2026': c['CARGO_2026'],
            'tse_cargo_2026': c['TSE_CARGO_2026'],
            'cargo_base_label': c['TSE_CARGO_BASE_LABEL'],
            'ano_base': c['TSE_ANO_BASE'],
            'uf': c['UF'],
            'cores': c['CORES'],
        }
    }
