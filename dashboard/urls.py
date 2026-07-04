from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('meta-votos/', views.meta_votos, name='meta_votos'),
    # Resumo da semana (antigo conteúdo da home) — preservado e acessível.
    path('semana/', login_required(views.home_view), name='painel_semana'),
]
