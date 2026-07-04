"""Limpeza de texto com IA (Claude Haiku 4.5) para o campo Observações.

Usado tanto no PWA (ponta, ao cadastrar) quanto na gestão das planilhas
(back-office, ao revisar leads e voluntários). É opcional: só funciona se
ANTHROPIC_API_KEY estiver configurada no servidor. Online apenas.

A limpeza é *conservadora*: corrige ortografia, pontuação e maiúsculas,
organiza a frase e remove ruído de transcrição — sem inventar informação
nem mudar o sentido. Se não houver nada a limpar, devolve o texto original.
"""
from django.conf import settings

# Limite defensivo de tamanho (observações são curtas; evita custo/abuso).
MAX_CHARS = 4000

SYSTEM_PROMPT = (
    "Você revisa anotações de uma equipe de campo de uma campanha política em "
    "Santa Catarina. As notas são curtas, escritas às pressas ou ditadas por voz, "
    "e descrevem apoiadores, lideranças e voluntários.\n\n"
    "Sua tarefa: devolver a MESMA anotação, apenas com português corrigido — "
    "ortografia, acentuação, pontuação e uso de maiúsculas — e com a frase "
    "organizada de forma clara e natural.\n\n"
    "Regras invioláveis:\n"
    "- NÃO invente, suponha nem acrescente qualquer informação que não esteja no texto.\n"
    "- NÃO remova fatos, nomes, números, telefones ou detalhes.\n"
    "- Preserve nomes próprios e nomes de cidades como estão (apenas corrija "
    "maiúsculas/acentos óbvios).\n"
    "- Mantenha o tom e a intenção originais; não deixe mais formal do que precisa.\n"
    "- Remova apenas ruído claro de transcrição (repetições, hesitações, "
    "'ãã', frases de fechamento automáticas como 'Obrigado pela atenção' que o "
    "transcritor adicionou sozinho).\n"
    "- Se o texto já estiver bom ou não houver o que corrigir, devolva-o igual.\n\n"
    "Responda SOMENTE com o texto corrigido, sem aspas, sem comentários, sem "
    "prefixos como 'Texto corrigido:'."
)


class IANaoConfigurada(Exception):
    """ANTHROPIC_API_KEY não está definida no servidor."""


class IAError(Exception):
    """Falha ao chamar a API (rede, limite, etc.)."""


def disponivel():
    return bool(getattr(settings, 'ANTHROPIC_API_KEY', ''))


def limpar_texto(texto):
    """Devolve `texto` revisado pela IA. Lança IANaoConfigurada/IAError em falha."""
    texto = (texto or '').strip()
    if not texto:
        return ''
    if len(texto) > MAX_CHARS:
        texto = texto[:MAX_CHARS]

    key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not key:
        raise IANaoConfigurada()

    model = getattr(settings, 'IA_LIMPEZA_MODEL', 'claude-haiku-4-5')

    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise IAError('SDK da Anthropic não instalado no servidor.') from e

    client = anthropic.Anthropic(api_key=key)
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': texto}],
        )
    except anthropic.APIError as e:
        raise IAError(str(e)[:200]) from e
    except Exception as e:  # noqa — rede/timeout
        raise IAError(str(e)[:200]) from e

    partes = [b.text for b in resp.content if getattr(b, 'type', None) == 'text']
    limpo = ''.join(partes).strip()
    return limpo or texto
