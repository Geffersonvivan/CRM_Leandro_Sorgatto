from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuario_list, name='list'),
    path('novo/', views.usuario_create, name='create'),
    path('<int:pk>/editar/', views.usuario_edit, name='edit'),
    path('<int:pk>/toggle/', views.usuario_toggle, name='toggle'),
    path('pwa/', views.usuario_pwa_list, name='pwa_list'),
    path('pwa/novo/', views.usuario_pwa_create, name='pwa_create'),
    path('pwa/<int:pk>/editar/', views.usuario_pwa_edit, name='pwa_edit'),
    path('api/cidades/<int:regiao_id>/', views.api_cidades_por_regiao, name='api_cidades'),
]
