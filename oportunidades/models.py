from django.conf import settings
from django.db import models
from django.utils import timezone


class Oportunidade(models.Model):
    """Oportunidade estratégica detectada (cidade onde vale investir o tempo do LS).

    É a memória persistente do que o painel 'Estratégia da semana' mostra de forma
    efêmera: nasce, é vista, vira ação (agendada) ou é descartada — sem repetir o
    que já foi tratado. `dedup_key` garante idempotência entre rodadas do detector.
    """

    TIPO = [
        ('territorio', 'Território'),          # cidade de alta oportunidade sem visita
        ('relacionamento', 'Relacionamento'),  # base forte/contatos sem visita marcada
        ('concorrencia', 'Concorrência'),      # rival comendo voto conservador (futuro)
        ('agenda', 'Agenda'),                  # dia livre, palanque conjunto (futuro)
        ('demanda', 'Demanda'),                # demanda/tarefa atrasada (futuro)
    ]
    STATUS = [
        ('nova', 'Nova'),
        ('vista', 'Vista'),
        ('em_andamento', 'Em andamento'),
        ('agendada', 'Agendada'),
        ('descartada', 'Descartada'),
        ('concluida', 'Concluída'),
        ('expirada', 'Expirada'),
    ]
    PRIORIDADE = [('alta', 'Alta'), ('media', 'Média'), ('baixa', 'Baixa')]
    FONTE = [('regra', 'Determinístico'), ('agente', 'Agente IA')]

    VIVAS = ('nova', 'vista', 'em_andamento')

    tipo = models.CharField(max_length=20, choices=TIPO, db_index=True)
    titulo = models.CharField(max_length=160)
    justificativa = models.TextField(blank=True)
    acao_sugerida = models.CharField(max_length=120, blank=True)

    cidade = models.ForeignKey('liderancas.Cidade', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='oportunidades')

    score = models.PositiveSmallIntegerField(default=0)
    prioridade = models.CharField(max_length=6, choices=PRIORIDADE, default='media', db_index=True)

    fonte = models.CharField(max_length=10, choices=FONTE, default='regra')
    agente = models.CharField(max_length=40, blank=True)
    evidencia = models.JSONField(default=dict, blank=True)
    dedup_key = models.CharField(max_length=120, db_index=True)
    ciclo = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=14, choices=STATUS, default='nova', db_index=True)
    atribuida_a = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='oportunidades')
    compromisso = models.ForeignKey('agenda.Compromisso', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='oportunidades')
    motivo_descarte = models.CharField(max_length=200, blank=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    vista_em = models.DateTimeField(null=True, blank=True)
    resolvida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Oportunidade'
        verbose_name_plural = 'Oportunidades'
        ordering = ['-score', '-criada_em']
        indexes = [models.Index(fields=['status', 'tipo', 'prioridade'])]
        constraints = [
            # uma oportunidade "viva" por chave — o detector faz upsert sem duplicar
            models.UniqueConstraint(
                fields=['dedup_key'],
                condition=models.Q(status__in=['nova', 'vista', 'em_andamento']),
                name='uniq_oportunidade_viva',
            ),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.titulo}'

    def marcar_resolvida(self, status):
        self.status = status
        self.resolvida_em = timezone.now()
        self.save(update_fields=['status', 'resolvida_em', 'atualizada_em'])
