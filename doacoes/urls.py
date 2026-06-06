from django.urls import path
from . import views

app_name = 'doacoes'

urlpatterns = [
    path('', views.doacao_list, name='doacao_list'),
    path('nova/', views.doacao_create, name='doacao_create'),
    path('<int:pk>/editar/', views.doacao_edit, name='doacao_edit'),
    path('<int:pk>/excluir/', views.doacao_delete, name='doacao_delete'),
    path('<int:pk>/detalhe/', views.doacao_detalhe, name='doacao_detalhe'),

    # Dashboard
    path('dashboard/', views.dashboard_doacoes, name='dashboard_doacoes'),

    # Comissões
    path('comissoes/', views.comissao_list, name='comissao_list'),
    path('comissoes/<int:pk>/pagar/', views.comissao_pagar, name='comissao_pagar'),

    # API
    path('api/cidades/<int:regiao_id>/', views.api_cidades_regiao, name='api_cidades_regiao'),
]
