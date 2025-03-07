from django.urls import path
from .views import *


app_name = 'polls'

urlpatterns = [
    path('', cargar_csv, name='cargar_csv'),
    path('cambiarhp/', cambiarhp, name='cambiarhp'),
    path('view/', mostrar_csv, name='mostrar_csv'),
    path('edit/', modificar_csv, name='modificar_csv'),
    path('update/', update, name='update'),
    path('todatabase/', columnas_seleccionadas, name='columnas_seleccionadas'),
    path('newtable/',nueva_tabla, name='nueva_tabla'),
    path('insert/',insertar_datos,name='insertar_datos')
]