"""Permissão por seção (CLAUDE.md §3.7 e §13.2): visibilidade e ação dependem
de Usuario.secoes_permitidas via pode_acessar (com herança pai→filhos) e do
decorator @secao_required."""
from django.test import TestCase, override_settings
from django.urls import reverse

from usuarios.models import Usuario

# Storage simples nos testes: o manifest do WhiteNoise (collectstatic) não
# existe no ambiente de teste e {% static %} falharia sem isto.
STORAGES_TESTE = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

class PodeAcessarTests(TestCase):
    def _user(self, **kw):
        kw.setdefault('password', 'x')
        return Usuario.objects.create_user(**kw)

    def test_admin_acessa_qualquer_secao(self):
        u = self._user(username='adm', perfil='admin')
        self.assertTrue(u.pode_acessar('liderancas'))
        self.assertTrue(u.pode_acessar('qualquer:coisa'))

    def test_secao_exata_permite(self):
        u = self._user(username='op1', secoes_permitidas=['mapa'])
        self.assertTrue(u.pode_acessar('mapa'))
        self.assertFalse(u.pode_acessar('liderancas'))

    def test_heranca_pai_da_acesso_aos_filhos(self):
        u = self._user(username='op2', secoes_permitidas=['liderancas'])
        self.assertTrue(u.pode_acessar('liderancas:lista'))
        self.assertTrue(u.pode_acessar('liderancas:aprovar'))

    def test_filho_nao_da_acesso_ao_pai_nem_a_irmaos(self):
        u = self._user(username='op3', secoes_permitidas=['liderancas:lista'])
        self.assertFalse(u.pode_acessar('liderancas'))
        self.assertFalse(u.pode_acessar('liderancas:aprovar'))

    def test_sem_secao_nega(self):
        u = self._user(username='op4', secoes_permitidas=[])
        self.assertFalse(u.pode_acessar('liderancas:lista'))


@override_settings(ALLOWED_HOSTS=['testserver'], STORAGES=STORAGES_TESTE)
class SecaoRequiredViewTests(TestCase):
    """Usuário com/sem a seção vê/não vê o recurso (§13.2), na rota real da
    lista unificada de Lideranças (@secao_required('liderancas:lista'))."""

    @classmethod
    def setUpTestData(cls):
        cls.com_acesso = Usuario.objects.create_user(
            username='ver', password='x', secoes_permitidas=['liderancas'])
        cls.sem_acesso = Usuario.objects.create_user(
            username='naove', password='x', secoes_permitidas=[])
        cls.url = reverse('liderancas:lideranca_list')

    def test_com_secao_ve_o_recurso(self):
        self.client.force_login(self.com_acesso)
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_sem_secao_e_redirecionado_para_home(self):
        self.client.force_login(self.sem_acesso)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('home'))

    def test_anonimo_vai_para_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_ajax_sem_secao_recebe_403_json(self):
        self.client.force_login(self.sem_acesso)
        resp = self.client.get(self.url, headers={'x-requested-with': 'XMLHttpRequest'})
        self.assertEqual(resp.status_code, 403)
        self.assertIn('error', resp.json())
