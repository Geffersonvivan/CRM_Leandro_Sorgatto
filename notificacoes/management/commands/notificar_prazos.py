from django.core.management.base import BaseCommand
from notificacoes.views import criar_notificacoes_prazo


class Command(BaseCommand):
    help = 'Envia notificações para tarefas com prazo vencendo hoje, amanhã ou vencidas.'

    def handle(self, *args, **options):
        criar_notificacoes_prazo()
        self.stdout.write(self.style.SUCCESS('Notificações de prazo enviadas.'))
