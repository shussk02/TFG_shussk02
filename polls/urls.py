from django.urls import path
from .views import *

urlpatterns = [
    path('index/',index, name='index'),
    path('', cargar_csv, name='cargar_csv'),
    path('csv/', mostrar_csv, name='mostrar_csv'),
]