import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory, override_settings

from liderancas.models import Regiao, Cidade
from .models import Evento, EventoAnexo
from .forms import EventoForm, ANEXO_MAX_BYTES
from . import views

MEDIA_TMP = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class EventoAnexoTests(TestCase):
    def setUp(self):
        self.regiao = Regiao.objects.create(nome='Oeste', sigla='OES')
        self.cidade = Cidade.objects.create(nome='Chapecó', regiao=self.regiao)
        self.evento = Evento.objects.create(
            nome='Festa', tipo='festa', data='2026-07-10', cidade=self.cidade,
        )

    def _upload(self, nome, tamanho=10):
        return SimpleUploadedFile(nome, b'x' * tamanho, content_type='application/octet-stream')

    def _form_data(self):
        return {
            'nome': 'Festa', 'tipo': 'festa', 'data': '2026-07-10',
            'regiao': self.regiao.id, 'cidade': self.cidade.id,
            'relevancia': 'media', 'status': 'identificado',
            'local': '', 'observacoes': '', 'resultado': '', 'publico_estimado': '',
        }

    def test_form_aceita_multiplos_anexos_validos(self):
        files = {'anexos': [self._upload('a.png'), self._upload('b.pdf')]}
        form = EventoForm(self._form_data(), files)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(len(form.cleaned_data['anexos']), 2)

    def test_form_rejeita_extensao_invalida(self):
        form = EventoForm(self._form_data(), {'anexos': [self._upload('malware.exe')]})
        self.assertFalse(form.is_valid())
        self.assertIn('anexos', form.errors)

    def test_form_rejeita_arquivo_grande(self):
        big = self._upload('grande.pdf', tamanho=ANEXO_MAX_BYTES + 1)
        form = EventoForm(self._form_data(), {'anexos': [big]})
        self.assertFalse(form.is_valid())
        self.assertIn('anexos', form.errors)

    def test_helper_cria_um_anexo_por_arquivo(self):
        files = {'anexos': [self._upload('a.png'), self._upload('b.pdf')]}
        form = EventoForm(self._form_data(), files)
        self.assertTrue(form.is_valid(), form.errors)
        req = RequestFactory().post('/')
        req.user = None  # enviado_por é null=True
        views._salvar_anexos_evento(req, form, self.evento)
        self.assertEqual(self.evento.anexos.count(), 2)

    def test_exclusao_remove_registro_e_arquivo(self):
        anexo = EventoAnexo.objects.create(evento=self.evento, arquivo=self._upload('x.pdf'))
        caminho = Path(anexo.arquivo.path)
        self.assertTrue(caminho.exists())
        anexo.arquivo.delete(save=False)
        anexo.delete()
        self.assertFalse(caminho.exists())
        self.assertFalse(EventoAnexo.objects.filter(pk=anexo.pk).exists())

    def test_is_imagem_property(self):
        img = EventoAnexo.objects.create(evento=self.evento, arquivo=self._upload('foto.PNG'))
        pdf = EventoAnexo.objects.create(evento=self.evento, arquivo=self._upload('doc.pdf'))
        self.assertTrue(img.is_imagem)
        self.assertFalse(pdf.is_imagem)
