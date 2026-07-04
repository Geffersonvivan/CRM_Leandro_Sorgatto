"""Config de marca — Isadora Piana (NOVO/30), Deputada Estadual · SC 2026.

Tudo que difere entre marcas e NÃO é segredo vive aqui (D10). O código lê
settings.CAMPANHA (ou o context processor `campanha` nos templates); nenhum
nome, número ou cargo pode ficar hardcodado fora deste arquivo.
"""

CAMPANHA = {
    'CANDIDATO_NOME': 'Isadora Piana',
    'CANDIDATO_PRIMEIRO_NOME': 'Isadora',
    'PARTIDO_SIGLA': 'NOVO',
    'PARTIDO_NUMERO': '30',
    'UF': 'Santa Catarina',

    # Cargo em disputa em 2026: rótulo humano e valor de máquina (chaves do
    # TSE usadas nos filtros do mapa — concorrência, ranking de ameaça).
    'CARGO_2026': 'Deputada Estadual',
    'TSE_CARGO_2026': 'deputado_estadual',

    # Base eleitoral de referência no mapa (votação do candidato em eleição
    # anterior). Pode divergir do cargo em disputa (ex.: federal→estadual).
    'TSE_TERMO_BUSCA': 'ISADORA',
    'TSE_CARGO_BASE': 'deputado_estadual',
    'TSE_ANO_BASE': 2022,

    # Cores da marca — valores das variáveis CSS históricas (--navy/--ouro/
    # --coral guardam a paleta atual; usar sempre a variável, não hex avulso).
    # Injetadas no :root pelo base.html; global.css traz o fallback.
    'CORES': {
        '--navy': '#FF6B00',        # laranja NOVO (marca)
        '--navy-700': '#E25E00',
        '--navy-900': '#2B2B2B',    # grafite — superfície escura
        '--ouro': '#C44B00',        # assinatura (fio/chip/realce, com moderação)
        '--ouro-strong': '#A33D00',
        '--coral': '#7c3aed',       # vertical Mobilização
        '--teal': '#0d9488',        # vertical Tarefas
    },

    # Colunas da lista de Lideranças, na ordem de exibição. O model guarda o
    # superset; cada marca lista aqui o que mostra (wiring do template na
    # Fase 2 — por ora documenta o contrato da Isadora, que exibe tudo).
    'COLUNAS_LIDERANCA': [
        'nome', 'cidade', 'telefone', 'email', 'instagram',
        'coordenador_responsavel', 'categoria', 'voto',
        'frequencia_relacionamento', 'votos_referencia', 'cadastrado_por',
        'uf', 'nivel', 'atendente', 'contato_feito', 'data_contato',
        'canal_atendimento', 'quem_e_eleitor', 'filiado_partido', 'segmentos',
        'idade', 'vaquinha_enviada', 'doou', 'material_entregue', 'facebook',
    ],
}
