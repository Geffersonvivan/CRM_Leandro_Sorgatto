"""Habilita a extensão `unaccent` no PostgreSQL (produção) para busca sem acento.
No SQLite (dev) é um no-op — a busca cai para icontains sensível a acento."""
from django.db import migrations


def criar_unaccent(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('CREATE EXTENSION IF NOT EXISTS unaccent')


def remover_unaccent(apps, schema_editor):
    # Não removemos a extensão (pode ser usada por outras buscas).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('liderancas', '0018_remove_interacaolog_apoiador_and_more'),
    ]

    operations = [
        migrations.RunPython(criar_unaccent, remover_unaccent),
    ]
