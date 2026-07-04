"""Copia CoordenadorRegional, CaboEleitoral e Apoiador para o modelo unificado
Lideranca, preservando timestamps de auditoria, soft-delete e a hierarquia
cabo -> coordenador (coordenador_responsavel)."""
from django.db import migrations


def copiar(apps, schema_editor):
    Coordenador = apps.get_model('liderancas', 'CoordenadorRegional')
    Cabo = apps.get_model('liderancas', 'CaboEleitoral')
    Apoiador = apps.get_model('liderancas', 'Apoiador')
    Lideranca = apps.get_model('liderancas', 'Lideranca')

    coord_map = {}  # pk antigo do coordenador -> pk novo na Lideranca

    # --- Coordenadores ---
    for c in Coordenador.objects.all():
        l = Lideranca.objects.create(
            papel='coordenador',
            nome=c.nome, telefone=c.telefone, email=c.email, instagram=c.instagram,
            cidade_id=c.cidade_base_id, regiao_id=c.regiao_id,
            prioridade=c.prioridade, frequencia_relacionamento=c.frequencia_relacionamento,
            observacoes=c.observacoes,
            cadastrado_por_id=c.cadastrado_por_id, atualizado_por_id=c.atualizado_por_id,
            is_active=c.is_active, deleted_at=c.deleted_at, deleted_by_id=c.deleted_by_id,
        )
        Lideranca.objects.filter(pk=l.pk).update(created_at=c.created_at, updated_at=c.updated_at)
        coord_map[c.id] = l.id

    # --- Cabos eleitorais (hierarquia via coord_map) ---
    for c in Cabo.objects.all():
        regiao_id = c.cidade.regiao_id if c.cidade_id else None
        l = Lideranca.objects.create(
            papel='cabo',
            nome=c.nome, telefone=c.telefone, email=c.email, instagram=c.instagram,
            cidade_id=c.cidade_id, regiao_id=regiao_id,
            coordenador_responsavel_id=coord_map.get(c.coordenador_id),
            prioridade=c.prioridade, frequencia_relacionamento=c.frequencia_relacionamento,
            observacoes=c.observacoes,
            cadastrado_por_id=c.cadastrado_por_id, atualizado_por_id=c.atualizado_por_id,
            is_active=c.is_active, deleted_at=c.deleted_at, deleted_by_id=c.deleted_by_id,
        )
        Lideranca.objects.filter(pk=l.pk).update(created_at=c.created_at, updated_at=c.updated_at)

    # --- Apoiadores (campos específicos) ---
    for a in Apoiador.objects.all():
        regiao_id = a.cidade.regiao_id if a.cidade_id else None
        l = Lideranca.objects.create(
            papel='apoiador',
            nome=a.nome, telefone=a.telefone, email=a.email, instagram=a.instagram,
            cidade_id=a.cidade_id, regiao_id=regiao_id,
            prioridade=a.prioridade, frequencia_relacionamento=a.frequencia_relacionamento,
            observacoes=a.observacoes,
            tipo=a.tipo, cargo=a.cargo,
            votos_referencia=a.votos_referencia, meta_votos_transferir=a.meta_votos_transferir,
            origem_contato=a.origem_contato, grau_influencia=a.grau_influencia, status=a.status,
            cadastrado_por_id=a.cadastrado_por_id, atualizado_por_id=a.atualizado_por_id,
            is_active=a.is_active, deleted_at=a.deleted_at, deleted_by_id=a.deleted_by_id,
        )
        Lideranca.objects.filter(pk=l.pk).update(created_at=a.created_at, updated_at=a.updated_at)


def reverter(apps, schema_editor):
    Lideranca = apps.get_model('liderancas', 'Lideranca')
    Lideranca.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('liderancas', '0016_lideranca'),
    ]

    operations = [
        migrations.RunPython(copiar, reverter),
    ]
