"""Config de marca (Fase 1 do ARQUITETURA_ROADMAP, decisão D10): o mesmo código
serve qualquer marca trocando só a config. Estes testes rodam o mecanismo sob
DUAS configs — a real (Isadora) e uma marca fictícia masculina com cargo federal —
para a troca de marca não regredir comportamento em silêncio."""
import json

from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.test import SimpleTestCase, TestCase, override_settings

from core.context_processors import campanha

# Marca fictícia de teste: masculina e com cargo em disputa diferente (federal),
# como o caso Sorgatto/Gilson — exercita artigo, cargo e cores vindos da config.
MARCA_TESTE = {
    'CANDIDATO_NOME': 'João Teste',
    'CANDIDATO_PRIMEIRO_NOME': 'João',
    'CANDIDATO_ARTIGO': 'o',
    'PARTIDO_SIGLA': 'NOVO',
    'PARTIDO_NUMERO': '30',
    'UF': 'Santa Catarina',
    'CARGO_2026': 'Deputado Federal',
    'TSE_CARGO_2026': 'deputado_federal',
    'TSE_TERMO_BUSCA': 'JOAO TESTE',
    'TSE_CARGO_BASE': 'deputado_federal',
    'TSE_CARGO_BASE_LABEL': 'Dep. Federal',
    'TSE_ANO_BASE': 2022,
    'CORES': {
        '--navy': '#112233', '--navy-700': '#101010', '--navy-900': '#0A0B0C',
        '--ouro': '#445566', '--ouro-strong': '#334455',
        '--coral': '#556677', '--teal': '#667788',
    },
    'COLUNAS_LIDERANCA': ['nome', 'cidade', 'telefone'],
}

# Storage simples nos testes: o manifest do WhiteNoise (collectstatic) não
# existe no ambiente de teste e {% static %} falharia sem isto.
STORAGES_TESTE = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

class ConfigIsadoraTests(SimpleTestCase):
    def test_config_carregada_de_configs_slug(self):
        # settings.CAMPANHA vem de configs/<MARCA>.py, não de env de branding
        import configs.isadora
        self.assertEqual(settings.CAMPANHA, configs.isadora.CAMPANHA)

    def test_chaves_obrigatorias_presentes(self):
        obrigatorias = {
            'CANDIDATO_NOME', 'CANDIDATO_PRIMEIRO_NOME', 'CANDIDATO_ARTIGO',
            'PARTIDO_SIGLA', 'PARTIDO_NUMERO', 'UF', 'CARGO_2026', 'TSE_CARGO_2026',
            'TSE_TERMO_BUSCA', 'TSE_CARGO_BASE', 'TSE_CARGO_BASE_LABEL',
            'TSE_ANO_BASE', 'CORES', 'COLUNAS_LIDERANCA',
        }
        self.assertTrue(obrigatorias.issubset(settings.CAMPANHA.keys()),
                        obrigatorias - set(settings.CAMPANHA.keys()))

    def test_colunas_lideranca_sao_campos_reais_do_model(self):
        # a lista da config referencia campos existentes (contrato p/ Fase 2)
        from liderancas.models import Lideranca
        campos = {f.name for f in Lideranca._meta.get_fields()}
        sobras = set(settings.CAMPANHA['COLUNAS_LIDERANCA']) - campos
        self.assertEqual(sobras, set())


class ContextProcessorGramaticaTests(SimpleTestCase):
    """As formas com artigo mantêm a gramática ao trocar o gênero da marca."""

    def test_marca_feminina(self):
        with override_settings(CAMPANHA=dict(settings.CAMPANHA)):
            c = campanha(None)['campanha']
        self.assertEqual(c['trat_nome'], 'a Isadora')
        self.assertEqual(c['de_nome'], 'da Isadora')
        self.assertEqual(c['em_nome'], 'na Isadora')
        self.assertEqual(c['a_nome'], 'à Isadora')

    @override_settings(CAMPANHA=MARCA_TESTE)
    def test_marca_masculina(self):
        c = campanha(None)['campanha']
        self.assertEqual(c['trat_nome'], 'o João')
        self.assertEqual(c['de_nome'], 'do João')
        self.assertEqual(c['em_nome'], 'no João')
        self.assertEqual(c['a_nome'], 'ao João')
        self.assertEqual(c['tse_cargo_2026'], 'deputado_federal')


@override_settings(STORAGES=STORAGES_TESTE)
class TemplateSobDuasMarcasTests(TestCase):
    """Zero string de marca hardcoded: os templates centrais renderizam a marca
    da config — inclusive o mapa (cargo em disputa) e as cores no :root."""

    def _render(self, nome_template):
        ctx = campanha(None)
        ctx.update({'user': None, 'request': None})
        return get_template(nome_template).template.render(Context(ctx))

    def test_mapa_usa_cargo_e_nome_da_config_isadora(self):
        html = self._render('mapa/index.html')
        self.assertIn("TSE_CARGO_2026 = 'deputado_estadual'", html.replace('"', "'"))
        self.assertIn('da Isadora', html)
        self.assertIn('Dep. Estadual', html)

    @override_settings(CAMPANHA=MARCA_TESTE)
    def test_mapa_sob_outra_marca_nao_vaza_isadora(self):
        html = self._render('mapa/index.html')
        self.assertIn("TSE_CARGO_2026 = 'deputado_federal'", html.replace('"', "'"))
        self.assertIn('do João', html)
        self.assertNotIn('Isadora', html)

    @override_settings(CAMPANHA=MARCA_TESTE)
    def test_base_html_injeta_cores_da_config(self):
        html = self._render('base.html')
        self.assertIn('--navy: #112233;', html)
        self.assertIn('CRM Eleitoral — João Teste', html)

    @override_settings(CAMPANHA=MARCA_TESTE)
    def test_pwa_shell_sob_outra_marca(self):
        html = self._render('pwa/base.html')
        self.assertIn('--navy: #112233;', html)
        self.assertNotIn('Isadora', html)


@override_settings(ALLOWED_HOSTS=['testserver'], STORAGES=STORAGES_TESTE)
class ManifestPorMarcaTests(TestCase):
    def test_manifest_isadora(self):
        m = json.loads(self.client.get('/app/manifest.json').content)
        self.assertEqual(m['short_name'], 'Isadora 30')
        self.assertIn('Isadora Piana', m['description'])

    @override_settings(CAMPANHA=MARCA_TESTE)
    def test_manifest_outra_marca(self):
        m = json.loads(self.client.get('/app/manifest.json').content)
        self.assertEqual(m['short_name'], 'João 30')
        self.assertEqual(m['theme_color'], '#0A0B0C')   # --navy-900 da config
        self.assertNotIn('Isadora', json.dumps(m, ensure_ascii=False))
