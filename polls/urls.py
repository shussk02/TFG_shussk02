from django.urls import path
from .views import *

urlpatterns = [
    path('index/',index, name='index'),
    path('', mostrar_csv, name='mostrar_csv'),

]