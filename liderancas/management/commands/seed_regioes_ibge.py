"""Semeia a regionalização IBGE de SC (6 mesorregiões + 20 microrregiões) e
mapeia cada município para a sua meso/microrregião via `codigo_ibge`.

Fonte: liderancas/data/ibge_sc_regioes.json (extraído da API oficial do IBGE —
servicodados.ibge.gov.br/.../estados/42/municipios). Dado real e verificável (§5).

Não mexe nas associações de municípios existentes (nível 'associacao'); só ADICIONA
os níveis meso/micro e preenche Cidade.mesorregiao/microrregiao. Idempotente.

Uso:
    python manage.py seed_regioes_ibge            # cria/atualiza + mapeia cidades
    python manage.py seed_regioes_ibge --geojson  # também agrega o geojson por região
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from liderancas.models import Cidade, Regiao

DADO = Path(settings.BASE_DIR) / 'liderancas' / 'data' / 'ibge_sc_regioes.json'


def _poligonos(geo):
    """Extrai a lista de polígonos (coords) de um geojson Polygon/MultiPolygon."""
    if not geo:
        return []
    t = geo.get('type')
    if t == 'Polygon':
        return [geo['coordinates']]
    if t == 'MultiPolygon':
        return list(geo['coordinates'])
    if t == 'Feature':
        return _poligonos(geo.get('geometry'))
    return []


class Command(BaseCommand):
    help = 'Semeia meso/microrregiões IBGE de SC e mapeia os municípios.'

    def add_arguments(self, parser):
        parser.add_argument('--geojson', action='store_true',
                            help='Agrega o geojson das regiões (MultiPolygon dos municípios).')

    @transaction.atomic
    def handle(self, *args, **opts):
        mapa = json.loads(DADO.read_text(encoding='utf-8'))

        # 1) Cria/atualiza as regiões meso e micro (idempotente por codigo+nivel).
        mesos, micros = {}, {}
        for cod, v in mapa.items():
            mesos.setdefault(str(v['meso_id']), v['meso'])
            micros.setdefault(str(v['micro_id']), v['micro'])

        def _upsert(codigo, nome, nivel):
            obj, _ = Regiao.objects.update_or_create(
                nivel=nivel, codigo=str(codigo),
                defaults={'nome': nome, 'sigla': nome[:20],
                          'slug': slugify(f'{nivel}-{nome}')[:50]},
            )
            return obj

        meso_por_id = {cid: _upsert(cid, nome, 'meso') for cid, nome in mesos.items()}
        micro_por_id = {cid: _upsert(cid, nome, 'micro') for cid, nome in micros.items()}
        self.stdout.write(f'Regiões: {len(meso_por_id)} meso, {len(micro_por_id)} micro.')

        # 2) Mapeia cada cidade (por codigo_ibge) para meso/micro.
        mapeadas, sem_match = 0, 0
        for c in Cidade.objects.all():
            info = mapa.get(str(c.codigo_ibge or '').strip())
            if not info:
                sem_match += 1
                continue
            c.mesorregiao = meso_por_id[str(info['meso_id'])]
            c.microrregiao = micro_por_id[str(info['micro_id'])]
            c.save(update_fields=['mesorregiao', 'microrregiao'])
            mapeadas += 1
        self.stdout.write(f'Cidades mapeadas: {mapeadas} (sem match IBGE: {sem_match}).')

        # 3) Geojson das regiões (opcional): MultiPolygon dos municípios membros.
        if opts['geojson']:
            for nivel, por_id, campo in (('meso', meso_por_id, 'mesorregiao'),
                                         ('micro', micro_por_id, 'microrregiao')):
                for reg in por_id.values():
                    polys = []
                    for cid in Cidade.objects.filter(**{campo: reg}).exclude(geojson__isnull=True):
                        polys.extend(_poligonos(cid.geojson))
                    reg.geojson = {'type': 'MultiPolygon', 'coordinates': polys} if polys else None
                    reg.save(update_fields=['geojson'])
            self.stdout.write('Geojson das regiões agregado.')

        self.stdout.write(self.style.SUCCESS('Seed IBGE concluído.'))
