"""Sync do PWA (CLAUDE.md §3.4, §6.2 e §13.3): reenviar a mesma fila offline
não duplica registros — a idempotência é por pwa_client_id, não por nome — e
todo cadastro de campo nasce pendente (origem pwa)."""
import json

from django.test import TestCase, override_settings
from django.urls import reverse

from liderancas.models import Lideranca, Voluntario
from liderancas.tests import criar_cidade
from usuarios.models import Usuario

# Storage simples nos testes: o manifest do WhiteNoise (collectstatic) não
# existe no ambiente de teste e {% static %} falharia sem isto.
STORAGES_TESTE = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

@override_settings(ALLOWED_HOSTS=['testserver'], STORAGES=STORAGES_TESTE)
class SyncApoiadorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidade = criar_cidade()
        cls.user = Usuario.objects.create_user(username='campo', password='x')
        cls.url = reverse('pwa:api_sync')

    def setUp(self):
        self.client.force_login(self.user)

    def _fila(self):
        return {'records': [
            {'client_id': 'uuid-aaa', 'nome': 'Apoiador Um', 'cidade_id': self.cidade.pk,
             'telefone': '(48) 99999-0001'},
            {'client_id': 'uuid-bbb', 'nome': 'Apoiador Dois', 'cidade_id': self.cidade.pk},
        ]}

    def _post(self, payload):
        return self.client.post(self.url, json.dumps(payload), content_type='application/json')

    def test_cadastro_de_campo_nasce_pendente_com_client_id(self):
        resp = self._post(self._fila())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Lideranca.objects.count(), 2)
        rec = Lideranca.objects.get(pwa_client_id='uuid-aaa')
        self.assertEqual(rec.aprovacao, 'pendente')   # §3.1: PWA nasce pendente
        self.assertEqual(rec.origem, 'pwa')
        self.assertEqual(rec.papel, 'apoiador')
        self.assertEqual(rec.cadastrado_por, self.user)
        # pendente não conta como oficial
        self.assertEqual(Lideranca.objects.apoiadores_aprovados().count(), 0)

    def test_categoria_multipla_e_opcional(self):
        # sync aceita lista de categorias; principal (tipo) = 1ª; inválidas caem fora
        self._post({'records': [
            {'client_id': 'm-1', 'nome': 'Multi', 'cidade_id': self.cidade.pk,
             'tipos': ['empresarial', 'associacao', 'inexistente']},
            {'client_id': 'm-2', 'nome': 'Sem Cat', 'cidade_id': self.cidade.pk, 'tipos': []},
        ]})
        multi = Lideranca.objects.get(pwa_client_id='m-1')
        self.assertEqual(multi.tipos, ['empresarial', 'associacao'])  # inválida removida
        self.assertEqual(multi.tipo, 'empresarial')                   # principal = 1ª
        sem = Lideranca.objects.get(pwa_client_id='m-2')
        self.assertEqual(sem.tipos, [])
        self.assertEqual(sem.tipo, '')                                # opcional: vazio

    def test_fila_antiga_com_tipo_unico_ainda_funciona(self):
        # aparelho não atualizado envia 'tipo' (string) — compat mantida
        self._post({'records': [{'client_id': 'old-1', 'nome': 'Legado',
                                 'cidade_id': self.cidade.pk, 'tipo': 'imprensa'}]})
        rec = Lideranca.objects.get(pwa_client_id='old-1')
        self.assertEqual(rec.tipos, ['imprensa'])
        self.assertEqual(rec.tipo, 'imprensa')

    def test_reenvio_da_mesma_fila_nao_duplica(self):
        self._post(self._fila())
        resp = self._post(self._fila())          # reenvio integral (ex.: app reabriu)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Lideranca.objects.count(), 2)
        # o aparelho recebe ok para poder limpar a fila local
        status = {r['client_id']: r['status'] for r in resp.json()['results']}
        self.assertEqual(status, {'uuid-aaa': 'ok', 'uuid-bbb': 'ok'})

    def test_mesmo_nome_com_client_id_diferente_cria_outro(self):
        # a chave é o client_id (§3.4) — homônimo real não é barrado aqui
        self._post({'records': [{'client_id': 'uuid-1', 'nome': 'João Silva',
                                 'cidade_id': self.cidade.pk}]})
        self._post({'records': [{'client_id': 'uuid-2', 'nome': 'João Silva',
                                 'cidade_id': self.cidade.pk}]})
        self.assertEqual(Lideranca.objects.filter(nome='João Silva').count(), 2)

    def test_sem_client_id_e_erro_no_registro(self):
        resp = self._post({'records': [{'nome': 'Sem Id', 'cidade_id': self.cidade.pk}]})
        self.assertEqual(resp.json()['results'][0]['status'], 'erro')
        self.assertEqual(Lideranca.objects.count(), 0)

    def test_nome_e_cidade_sao_obrigatorios(self):
        resp = self._post({'records': [{'client_id': 'uuid-x', 'nome': '', 'cidade_id': None}]})
        self.assertEqual(resp.json()['results'][0]['status'], 'erro')
        self.assertEqual(Lideranca.objects.count(), 0)

    def test_json_invalido_da_400(self):
        resp = self.client.post(self.url, 'não é json', content_type='application/json')
        self.assertEqual(resp.status_code, 400)     # §8.2: erro não devolve 200
        self.assertIn('error', resp.json())

    def test_anonimo_e_redirecionado_para_login_do_pwa(self):
        self.client.logout()
        resp = self._post(self._fila())
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Lideranca.objects.count(), 0)


@override_settings(ALLOWED_HOSTS=['testserver'], STORAGES=STORAGES_TESTE)
class SyncVoluntarioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidade = criar_cidade()
        cls.user = Usuario.objects.create_user(username='campo2', password='x')
        cls.url = reverse('pwa:api_sync_voluntario')

    def _post(self, payload):
        return self.client.post(self.url, json.dumps(payload), content_type='application/json')

    def test_reenvio_nao_duplica_e_nasce_pendente(self):
        self.client.force_login(self.user)
        fila = {'records': [{'client_id': 'vol-1', 'nome': 'Vera Voluntária',
                             'telefone': '(48) 98888-0001', 'cidade_id': self.cidade.pk,
                             'disponibilidades': ['panfletagem']}]}
        self._post(fila)
        self._post(fila)
        self.assertEqual(Voluntario.objects.count(), 1)
        vol = Voluntario.objects.get()
        self.assertEqual(vol.aprovacao, 'pendente')
        self.assertEqual(vol.origem, 'pwa')
