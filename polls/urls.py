from django.urls import path
from .views import *

urlpatterns = [
    path('index/',index, name='index'),
    path('upload/', cargar_csv, name='cargar_csv'),
    path('load/', mostrar_csv, name='mostrar_csv'),
    path('update/', update, name='update'),
]