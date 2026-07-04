from django.urls import path
from . import views

app_name = 'liderancas'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Lista unificada de Lideranças (com filtro por papel)
    path('', views.lideranca_list, name='lideranca_list'),
    path('bulk/', views.lideranca_bulk_action, name='lideranca_bulk'),

    # Coordenadores Regionais
    path('coordenadores/', views.coordenador_list, name='coordenador_list'),
    path('coordenadores/novo/', views.coordenador_create, name='coordenador_create'),
    path('coordenadores/<int:pk>/editar/', views.coordenador_edit, name='coordenador_edit'),
    path('coordenadores/<int:pk>/excluir/', views.coordenador_delete, name='coordenador_delete'),

    # Cabos Eleitorais
    path('cabos/', views.cabo_list, name='cabo_list'),
    path('cabos/novo/', views.cabo_create, name='cabo_create'),
    path('cabos/<int:pk>/editar/', views.cabo_edit, name='cabo_edit'),
    path('cabos/<int:pk>/excluir/', views.cabo_delete, name='cabo_delete'),

    # Apoiadores
    path('apoiadores/', views.apoiador_list, name='apoiador_list'),
    path('apoiadores/novo/', views.apoiador_create, name='apoiador_create'),
    path('apoiadores/<int:pk>/editar/', views.apoiador_edit, name='apoiador_edit'),
    path('apoiadores/<int:pk>/excluir/', views.apoiador_delete, name='apoiador_delete'),

    # Mobilização
    path('mobilizacao/', views.mobilizacao_list, name='mobilizacao_list'),
    path('mobilizacao/novo/', views.mobilizacao_create, name='mobilizacao_create'),
    path('mobilizacao/<int:pk>/editar/', views.mobilizacao_edit, name='mobilizacao_edit'),
    path('mobilizacao/<int:pk>/excluir/', views.mobilizacao_delete, name='mobilizacao_delete'),
    path('mobilizacao/bulk/', views.mobilizacao_bulk, name='mobilizacao_bulk'),

    # Ações em massa
    path('bulk-action/', views.bulk_action, name='bulk_action'),

    # Interações
    path('interacao/<str:entidade_tipo>/<int:pk>/nova/', views.interacao_add, name='interacao_add'),
    path('interacao/<str:entidade_tipo>/<int:pk>/ajax/', views.interacao_add_ajax, name='interacao_add_ajax'),
    path('interacao/<str:entidade_tipo>/<int:pk>/lista/', views.interacao_list, name='interacao_list'),

    # CSV Import
    path('importar/<str:entidade_tipo>/', views.csv_import, name='csv_import'),

    # API cidades por região (para JS dinâmico)
    path('api/cidades/<int:regiao_id>/', views.api_cidades, name='api_cidades'),
    # API mapa região→cidades (tooltip de cidades ao passar o mouse na região)
    path('api/regioes-cidades/', views.api_regioes_cidades, name='api_regioes_cidades'),

    # Limpeza de Observações com IA (Claude)
    path('api/limpar/', views.api_limpar_texto, name='api_limpar'),
    path('api/limpar-salvar/', views.api_limpar_salvar, name='api_limpar_salvar'),
]
