"""
Detector determinístico de oportunidades (Fase 1: Território + Relacionamento).

Cruza a oportunidade eleitoral (déficit de penetração × eleitorado, em log) com a
cobertura da agenda. Faz UPSERT por dedup_key (idempotente — pode rodar todo dia
sem duplicar) e resolve as que já foram cobertas (cidade ganhou compromisso).

    python manage.py detectar_oportunidades
    python manage.py detectar_oportunidades --dry-run
"""
import math
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from liderancas.models import Cidade, Apoiador
from agenda.models import Compromisso, Evento
from oportunidades.models import Oportunidade

TERR_MIN_SCORE = 40   # só vira oportunidade de território a partir deste score
TERR_MAX = 50         # teto de oportunidades de território por rodada


def _prioridade(score):
    return 'alta' if score >= 66 else 'media' if score >= 33 else 'baixa'


class Command(BaseCommand):
    help = 'Detecta oportunidades de Território e Relacionamento (determinístico)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        dry = opts['dry_run']
        hoje = timezone.localdate()
        ciclo = hoje

        cidades = list(Cidade.objects.select_related('regiao').all())
        ap = {r['cidade_id']: r['n'] for r in
              Apoiador.objects.filter(status='ativo').values('cidade_id').annotate(n=models.Count('id'))}

        comp_fut = set()
        for c in Compromisso.objects.exclude(status='cancelado').only('cidade_id', 'data_hora_inicio'):
            if c.cidade_id and timezone.localtime(c.data_hora_inicio).date() >= hoje:
                comp_fut.add(c.cidade_id)
        for e in Evento.objects.exclude(status='descartado').only('cidade_id', 'data'):
            if e.cidade_id and e.data >= hoje:
                comp_fut.add(e.cidade_id)

        pens = [c.votos_sorgatto_2022 / c.eleitores for c in cidades if c.eleitores]
        maxpen = max(pens) if pens else 1
        tot_v = sum(c.votos_sorgatto_2022 for c in cidades)
        tot_e = sum(c.eleitores for c in cidades) or 1
        avg_pen = tot_v / tot_e
        max_ap = max(ap.values(), default=1) or 1

        rows, maxopp = [], 0.0
        for c in cidades:
            pen = (c.votos_sorgatto_2022 / c.eleitores) if c.eleitores else 0
            deficit = max(0.0, 1 - (pen / maxpen if maxpen else 0))
            opp = deficit * math.log10((c.eleitores or 0) + 10)  # log: cidade média sobe
            maxopp = max(maxopp, opp)
            rows.append({'c': c, 'pen': pen, 'opp': opp, 'ap': ap.get(c.id, 0),
                         'fut': c.id in comp_fut})
        maxopp = maxopp or 1
        for r in rows:
            r['opp100'] = round(r['opp'] / maxopp * 100)

        detectadas = {}  # dedup_key -> dict(payload)

        # ── Território: alta oportunidade SEM visita futura ──
        terr = sorted((r for r in rows if not r['fut'] and r['opp100'] >= TERR_MIN_SCORE),
                      key=lambda r: r['opp'], reverse=True)[:TERR_MAX]
        for r in terr:
            c = r['c']
            if r['ap'] == 0:
                just = 'Muito voto a conquistar e presença zero — terreno virgem.'
            elif r['pen'] < avg_pen:
                just = 'Penetração abaixo da média — muito voto à mesa.'
            else:
                just = 'Alta oportunidade e ainda sem visita marcada.'
            detectadas[f'territorio:{c.id}'] = {
                'tipo': 'territorio', 'cidade': c, 'score': r['opp100'],
                'titulo': f'{c.nome}: {c.eleitores:,} eleitores · {r["ap"]} apoiador(es) · pen {round(r["pen"]*100,1)}%'.replace(',', '.'),
                'justificativa': just,
                'evidencia': {'eleitores': c.eleitores, 'penetracao': round(r['pen']*100, 1),
                              'apoiadores': r['ap'], 'regiao': c.regiao.nome if c.regiao_id else ''},
            }

        # ── Relacionamento: base forte com apoiadores e SEM visita futura (esfriando) ──
        esf = sorted((r for r in rows if r['pen'] >= avg_pen and r['ap'] > 0 and not r['fut']),
                     key=lambda r: r['ap'], reverse=True)
        for r in esf:
            c = r['c']
            score = round(min(r['ap'] / max_ap, 1) * 100)
            detectadas[f'relacionamento:{c.id}'] = {
                'tipo': 'relacionamento', 'cidade': c, 'score': score,
                'titulo': f'{c.nome}: base forte (pen {round(r["pen"]*100,1)}%) · {r["ap"]} apoiadores sem visita marcada',
                'justificativa': 'Reduto seu esfriando: tem estrutura, mas nenhuma visita à frente. Mantenha o relacionamento.',
                'evidencia': {'eleitores': c.eleitores, 'penetracao': round(r['pen']*100, 1),
                              'apoiadores': r['ap'], 'regiao': c.regiao.nome if c.regiao_id else ''},
            }

        criadas = atualizadas = resolvidas = 0
        if not dry:
            vivas = {o.dedup_key: o for o in Oportunidade.objects.filter(status__in=Oportunidade.VIVAS)}
            for key, d in detectadas.items():
                o = vivas.get(key)
                if o:  # upsert: atualiza dados, preserva status (nova/vista)
                    o.score = d['score']; o.prioridade = _prioridade(d['score'])
                    o.titulo = d['titulo']; o.justificativa = d['justificativa']
                    o.evidencia = d['evidencia']; o.ciclo = ciclo
                    o.save(update_fields=['score', 'prioridade', 'titulo', 'justificativa',
                                          'evidencia', 'ciclo', 'atualizada_em'])
                    atualizadas += 1
                else:
                    Oportunidade.objects.create(
                        tipo=d['tipo'], cidade=d['cidade'], score=d['score'],
                        prioridade=_prioridade(d['score']), titulo=d['titulo'],
                        justificativa=d['justificativa'], acao_sugerida='Agendar visita',
                        evidencia=d['evidencia'], dedup_key=key, ciclo=ciclo,
                        fonte='regra', status='nova',
                    )
                    criadas += 1
            # resolve as vivas que não foram re-detectadas (cidade coberta ou não qualifica mais)
            for key, o in vivas.items():
                if key not in detectadas:
                    novo = 'agendada' if (o.cidade_id in comp_fut) else 'expirada'
                    o.marcar_resolvida(novo)
                    resolvidas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Detectadas: {len(detectadas)} ({sum(1 for d in detectadas.values() if d["tipo"]=="territorio")} território, '
            f'{sum(1 for d in detectadas.values() if d["tipo"]=="relacionamento")} relacionamento). '
            + ('(dry-run)' if dry else f'criadas {criadas}, atualizadas {atualizadas}, resolvidas {resolvidas}.')))
