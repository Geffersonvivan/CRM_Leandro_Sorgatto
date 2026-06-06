from django.db import models
from django.conf import settings
from decimal import Decimal


class Doacao(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('pix', 'PIX'),
        ('cartao', 'Cartão de Crédito'),
        ('transferencia', 'Transferência Bancária'),
        ('dinheiro', 'Dinheiro'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('estornada', 'Estornada'),
    ]

    # Dados do doador
    doador_nome = models.CharField('Nome do doador', max_length=200)
    doador_cpf = models.CharField('CPF do doador', max_length=14)
    doador_telefone = models.CharField('Telefone', max_length=20, blank=True)
    doador_email = models.EmailField('E-mail', blank=True)

    # Valor e pagamento
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    data = models.DateTimeField('Data da doação')
    forma_pagamento = models.CharField(
        'Forma de pagamento', max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES, default='pix',
    )
    status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES, default='pendente',
    )
    comprovante = models.FileField(
        'Comprovante', upload_to='doacoes/comprovantes/',
        blank=True, null=True,
    )

    # Vínculo com a rede
    apoiador = models.ForeignKey(
        'liderancas.Apoiador', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='doacoes',
        verbose_name='Apoiador responsável',
    )
    coordenador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='doacoes_coordenadas',
        verbose_name='Coordenador',
    )
    regiao = models.ForeignKey(
        'liderancas.Regiao', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='doacoes',
    )
    cidade = models.ForeignKey(
        'liderancas.Cidade', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='doacoes',
    )

    # Comissões (calculadas automaticamente)
    comissao_plataforma = models.DecimalField(
        'Comissão plataforma (10%)', max_digits=10,
        decimal_places=2, default=0,
    )
    comissao_coordenador = models.DecimalField(
        'Comissão coordenador (7%)', max_digits=10,
        decimal_places=2, default=0,
    )
    comissao_apoiador = models.DecimalField(
        'Comissão apoiador (3%)', max_digits=10,
        decimal_places=2, default=0,
    )
    valor_liquido = models.DecimalField(
        'Valor líquido campanha (80%)', max_digits=10,
        decimal_places=2, default=0,
    )

    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doação'
        verbose_name_plural = 'Doações'
        ordering = ['-data']

    def __str__(self):
        return f'{self.doador_nome} - R$ {self.valor} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        self.calcular_comissoes()
        self.preencher_coordenador()
        super().save(*args, **kwargs)
        if self.status == 'confirmada':
            self.gerar_comissoes()

    def gerar_comissoes(self):
        # Comissão coordenador
        if self.coordenador and self.comissao_coordenador > 0:
            ComissaoResgate.objects.get_or_create(
                tipo='coordenador',
                coordenador=self.coordenador,
                valor=self.comissao_coordenador,
                defaults={'observacoes': f'Doação #{self.pk} - {self.doador_nome}'},
            )
        # Comissão apoiador
        if self.apoiador and self.comissao_apoiador > 0:
            ComissaoResgate.objects.get_or_create(
                tipo='apoiador',
                apoiador=self.apoiador,
                valor=self.comissao_apoiador,
                defaults={'observacoes': f'Doação #{self.pk} - {self.doador_nome}'},
            )

    def calcular_comissoes(self):
        if self.valor:
            self.comissao_plataforma = self.valor * Decimal('0.10')
            self.comissao_coordenador = self.valor * Decimal('0.07')
            self.comissao_apoiador = self.valor * Decimal('0.03')
            self.valor_liquido = self.valor * Decimal('0.80')

    def preencher_coordenador(self):
        if not self.coordenador and self.regiao:
            from usuarios.models import Usuario
            coord = Usuario.objects.filter(
                perfil='coordenador', regiao=self.regiao,
            ).first()
            if coord:
                self.coordenador = coord


class ComissaoResgate(models.Model):
    TIPO_CHOICES = [
        ('coordenador', 'Coordenador'),
        ('apoiador', 'Apoiador'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]

    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    coordenador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resgates_comissao',
        verbose_name='Coordenador',
    )
    apoiador = models.ForeignKey(
        'liderancas.Apoiador', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resgates_comissao',
        verbose_name='Apoiador',
    )
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES, default='pendente',
    )
    data_solicitacao = models.DateTimeField('Data da solicitação', auto_now_add=True)
    data_pagamento = models.DateTimeField('Data do pagamento', null=True, blank=True)
    nota_fiscal = models.FileField(
        'Nota fiscal', upload_to='doacoes/notas_fiscais/',
        blank=True, null=True,
    )
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Resgate de Comissão'
        verbose_name_plural = 'Resgates de Comissão'
        ordering = ['-data_solicitacao']

    def __str__(self):
        beneficiario = self.coordenador or self.apoiador
        return f'Resgate {self.get_tipo_display()} - R$ {self.valor} ({self.get_status_display()})'
