"""Moderação e soft-delete da rede (CLAUDE.md §3 e §13.1):
- pendente → aprovado | rejeitado; rejeitado → aprovado só por ação explícita;
- contagens oficiais só consideram aprovado; rejeitado some das listas padrão;
- rejeição registra motivo e autor; exclusão de negócio é soft-delete."""
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from liderancas.models import Cidade, Lideranca, Regiao
from usuarios.models import Usuario

# Storage simples nos testes: o manifest do WhiteNoise (collectstatic) não
# existe no ambiente de teste e {% static %} falharia sem isto.
STORAGES_TESTE = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

def criar_cidade(nome='Cidade Teste', **kw):
    regiao, _ = Regiao.objects.get_or_create(sigla='TST', defaults={'nome': 'Região Teste'})
    kw.setdefault('populacao', 1000)
    kw.setdefault('eleitores', 800)
    return Cidade.objects.create(nome=nome, regiao=regiao, **kw)


def criar_apoiador(cidade, nome, aprovacao='aprovado', **kw):
    kw.setdefault('status', 'ativo')
    kw.setdefault('origem', 'crm')
    return Lideranca.objects.create(
        papel='apoiador', nome=nome, cidade=cidade, regiao=cidade.regiao,
        aprovacao=aprovacao, **kw)


@override_settings(ALLOWED_HOSTS=['testserver'], STORAGES=STORAGES_TESTE)
class ModeracaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidade = criar_cidade()
        cls.moderador = Usuario.objects.create_user(
            username='mod', password='x', secoes_permitidas=['liderancas'])
        cls.bulk_url = reverse('liderancas:lideranca_bulk')

    def setUp(self):
        self.aprovado = criar_apoiador(self.cidade, 'Ana Aprovada')
        self.pendente = criar_apoiador(self.cidade, 'Pedro Pendente', aprovacao='pendente')
        self.rejeitado = criar_apoiador(self.cidade, 'Rui Rejeitado', aprovacao='rejeitado',
                                        motivo_rejeicao='duplicado')

    def test_contagem_oficial_so_conta_aprovado(self):
        # §3.1: placar/mapa/export usam o manager canônico, que exclui pendente/rejeitado
        oficiais = Lideranca.objects.apoiadores_aprovados()
        self.assertEqual(oficiais.count(), 1)
        self.assertEqual(oficiais.get().nome, 'Ana Aprovada')

    def test_lista_padrao_esconde_rejeitado(self):
        # §3.2: rejeitados não aparecem sem filtro explícito
        self.client.force_login(self.moderador)
        resp = self.client.get(reverse('liderancas:lideranca_list'))
        self.assertContains(resp, 'Ana Aprovada')
        self.assertContains(resp, 'Pedro Pendente')
        self.assertNotContains(resp, 'Rui Rejeitado')

    def test_filtro_explicito_mostra_rejeitados(self):
        self.client.force_login(self.moderador)
        resp = self.client.get(reverse('liderancas:lideranca_list'), {'aprovacao': 'rejeitado'})
        self.assertContains(resp, 'Rui Rejeitado')
        self.assertNotContains(resp, 'Ana Aprovada')

    def _bulk(self, action, alvo, **extra):
        return self.client.post(self.bulk_url, {
            'bulk_action': action, 'selected_ids': [alvo.pk], **extra})

    def test_aprovar_muda_estado_e_registra_autor(self):
        self.client.force_login(self.moderador)
        self._bulk('aprovar', self.pendente)
        self.pendente.refresh_from_db()
        self.assertEqual(self.pendente.aprovacao, 'aprovado')
        self.assertEqual(self.pendente.aprovado_por, self.moderador)
        self.assertIsNotNone(self.pendente.aprovado_em)
        self.assertEqual(Lideranca.objects.apoiadores_aprovados().count(), 2)

    def test_rejeitar_registra_motivo_e_autor(self):
        self.client.force_login(self.moderador)
        self._bulk('rejeitar', self.pendente, motivo_rejeicao='telefone inválido')
        self.pendente.refresh_from_db()
        self.assertEqual(self.pendente.aprovacao, 'rejeitado')
        self.assertEqual(self.pendente.motivo_rejeicao, 'telefone inválido')
        self.assertEqual(self.pendente.aprovado_por, self.moderador)
        # rejeitado não entra na contagem oficial
        self.assertEqual(Lideranca.objects.apoiadores_aprovados().count(), 1)

    def test_reverter_rejeitado_e_acao_explicita(self):
        # §3.2: rejeitado → aprovado só por ação explícita; limpa o motivo
        self.client.force_login(self.moderador)
        self._bulk('aprovar', self.rejeitado)
        self.rejeitado.refresh_from_db()
        self.assertEqual(self.rejeitado.aprovacao, 'aprovado')
        self.assertEqual(self.rejeitado.motivo_rejeicao, '')

    def test_sem_permissao_de_aprovacao_nao_muda_estado(self):
        # usuário só com a seção da lista (sem liderancas:aprovar, sem herança do pai)
        limitado = Usuario.objects.create_user(
            username='lim', password='x', secoes_permitidas=['liderancas:lista'])
        self.client.force_login(limitado)
        self._bulk('aprovar', self.pendente)
        self.pendente.refresh_from_db()
        self.assertEqual(self.pendente.aprovacao, 'pendente')


@override_settings(ALLOWED_HOSTS=['testserver'], STORAGES=STORAGES_TESTE)
class SoftDeleteTests(TestCase):
    """§3.6: entidades de negócio usam soft_delete(); nunca DELETE físico."""

    @classmethod
    def setUpTestData(cls):
        cls.cidade = criar_cidade()
        cls.user = Usuario.objects.create_user(
            username='mod2', password='x', secoes_permitidas=['liderancas'])

    def test_soft_delete_esconde_sem_apagar(self):
        pessoa = criar_apoiador(self.cidade, 'Sofia Some')
        pessoa.soft_delete(user=self.user)
        self.assertEqual(Lideranca.objects.filter(pk=pessoa.pk).count(), 0)
        salvo = Lideranca.all_objects.get(pk=pessoa.pk)
        self.assertFalse(salvo.is_active)
        self.assertIsNotNone(salvo.deleted_at)

    def test_bulk_delete_e_soft(self):
        pessoa = criar_apoiador(self.cidade, 'Bruno Bulk')
        self.client.force_login(self.user)
        self.client.post(reverse('liderancas:lideranca_bulk'), {
            'bulk_action': 'delete', 'selected_ids': [pessoa.pk]})
        # sumiu da lista, mas o registro físico continua lá
        self.assertEqual(Lideranca.objects.filter(pk=pessoa.pk).count(), 0)
        self.assertEqual(Lideranca.all_objects.filter(pk=pessoa.pk).count(), 1)
