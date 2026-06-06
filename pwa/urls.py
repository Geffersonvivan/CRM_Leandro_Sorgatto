from django.urls import path
from . import views

app_name = 'pwa'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.pwa_login, name='login'),
    path('logout/', views.pwa_logout, name='logout'),
    path('apoiador/novo/', views.cadastro_apoiador, name='cadastro_apoiador'),
    path('replicador/novo/', views.cadastro_replicador, name='cadastro_replicador'),
    path('mobilizacao/novo/', views.cadastro_voluntario, name='cadastro_voluntario'),
    path('doacao/nova/', views.cadastro_doacao, name='cadastro_doacao'),
    path('api/cidades/<int:regiao_id>/', views.api_cidades, name='api_cidades'),
    path('manifest.json', views.manifest_json, name='manifest'),
    path('sw.js', views.service_worker, name='sw'),
]
