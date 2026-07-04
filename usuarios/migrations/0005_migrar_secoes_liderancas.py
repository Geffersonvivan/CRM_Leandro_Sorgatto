"""Converte as seções antigas de Lideranças (apoiadores/cabos/coordenador) na
nova seção unificada 'liderancas:lista' nas permissões salvas dos usuários."""
from django.db import migrations

ANTIGAS = {'liderancas:apoiadores', 'liderancas:cabos_eleitorais', 'liderancas:coordenador_regional'}
NOVA = 'liderancas:lista'


def migrar(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    for u in Usuario.objects.all():
        secoes = u.secoes_permitidas or []
        if not isinstance(secoes, list) or not (ANTIGAS & set(secoes)):
            continue
        novas = [s for s in secoes if s not in ANTIGAS]
        if NOVA not in novas:
            novas.append(NOVA)
        u.secoes_permitidas = novas
        u.save(update_fields=['secoes_permitidas'])


def reverter(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_alter_usuario_regiao'),
    ]

    operations = [
        migrations.RunPython(migrar, reverter),
    ]
