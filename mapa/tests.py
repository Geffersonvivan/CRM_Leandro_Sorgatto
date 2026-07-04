"""Integridade dos indicadores do mapa (CLAUDE.md §5 e §13.4):
- rótulo bate com valor/unidade (pib_per_capita em R$ por habitante);
- sem dado → sem dado, excluído do cálculo (nunca preenchido por proxy);
- sanidade dos dados base (população > 0) é erro crítico;
- a auditoria de correlação acusa indicador sintético (derivado do PIB)."""
import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from liderancas.models import Cidade, Regiao
from mapa.models import IndicadorMunicipal


def criar_cidade(nome, populacao=1000, eleitores=800):
    regiao, _ = Regiao.objects.get_or_create(sigla='TST', defaults={'nome': 'Região Teste'})
    return Cidade.objects.create(nome=nome, regiao=regiao, slug=nome.lower().replace(' ', '-'),
                                 codigo_ibge=f'42{abs(hash(nome)) % 10**5:05d}',
                                 populacao=populacao, eleitores=eleitores)


class PibPerCapitaTests(TestCase):
    """§5.3: o que está rotulado 'PIB per capita' é PIB ÷ população, na unidade
    exibida (R$ por habitante) — `pib` é armazenado em R$ mil."""

    def test_unidade_reais_por_habitante(self):
        cidade = criar_cidade('Unidade', populacao=10_000)
        ind = IndicadorMunicipal.objects.create(
            cidade=cidade, ano_referencia=2022, populacao=10_000, pib=50_000)  # R$ 50 milhões
        self.assertEqual(ind.pib_per_capita, 5_000.0)  # R$ 5.000/hab, não 5 nem 5.000.000

    def test_sem_populacao_e_sem_dado_nao_zero(self):
        # §5.2: sem dado → None (excluído do cálculo), nunca um número inventado
        cidade = criar_cidade('Sem Pop')
        ind = IndicadorMunicipal.objects.create(
            cidade=cidade, ano_referencia=2022, populacao=0, pib=50_000)
        self.assertIsNone(ind.pib_per_capita)


class AuditoriaIndicadoresTests(TestCase):
    """O comando auditar_indicadores é o guarda-costas da Seção 5."""

    def _rodar(self, *args):
        out = StringIO()
        codigo = 0
        try:
            call_command('auditar_indicadores', '--json', *args, stdout=out)
        except SystemExit as e:
            codigo = e.code or 0
        return json.loads(out.getvalue()[:out.getvalue().rfind('}') + 1]), codigo

    def test_populacao_invalida_e_critica(self):
        # §5.6: população <= 0 distorce todo per capita — é erro de dado, crítico
        cidade = criar_cidade('Pop Zero', populacao=0)
        IndicadorMunicipal.objects.create(cidade=cidade, ano_referencia=2022,
                                          populacao=0, pib=100)
        report, codigo = self._rodar()
        self.assertEqual(codigo, 1)
        self.assertTrue(any('populacao' in c for c in report['criticos']))

    def test_indicador_sintetico_e_acusado(self):
        # §5.5: renda derivada do PIB per capita (r ≈ 1) não é sinal independente
        for i in range(10):
            pop = 1_000 + i * 500
            pib = 2_000 + (i * 37) % 900 * 10          # variação não monotônica
            IndicadorMunicipal.objects.create(
                cidade=criar_cidade(f'Sint {i}', populacao=pop),
                ano_referencia=2022, populacao=pop, pib=pib,
                renda_per_capita=round(float(pib) / pop * 0.5, 2),  # proxy disfarçado
                familias_bolsa_familia=(i * 7) % 13 + 1,
                meis_ativos=(i * 5) % 11 + 1,
                populacao_urbana=pop // 2, populacao_rural=pop - pop // 2,
                idosos_60_mais=(i * 3) % 9 + 1, jovens_18_29=(i * 11) % 17 + 1,
                anos_estudo_medio=5 + (i % 7),
            )
        report, _ = self._rodar()
        self.assertGreaterEqual(abs(report['metricas']['correlacao_pib']['renda_per_capita']), 0.90)
        self.assertTrue(any('renda_per_capita' in a and 'SINTÉTICO' in a
                            for a in report['avisos']))

    def test_dados_sadios_passam_sem_critico(self):
        cidade = criar_cidade('Sadia', populacao=20_000, eleitores=15_000)
        IndicadorMunicipal.objects.create(
            cidade=cidade, ano_referencia=2022, populacao=20_000, pib=80_000,
            renda_per_capita=1_500, familias_bolsa_familia=900, meis_ativos=700,
            populacao_urbana=15_000, populacao_rural=5_000,
            idosos_60_mais=3_000, jovens_18_29=4_000, anos_estudo_medio=9.1)
        report, codigo = self._rodar()
        self.assertEqual(codigo, 0)
        self.assertEqual(report['criticos'], [])
