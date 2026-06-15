from django.urls import path

from . import views

app_name = 'oportunidades'

urlpatterns = [
    path('', views.central, name='central'),
    path('<int:pk>/agendar/', views.agendar, name='agendar'),
    path('<int:pk>/descartar/', views.descartar, name='descartar'),
]
