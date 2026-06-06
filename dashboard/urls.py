from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('meta-votos/', views.meta_votos, name='meta_votos'),
]
