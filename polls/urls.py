from django.urls import path
from .views import *

urlpatterns = [
    path('index/',index, name='index'),
    path('', upload_csv, name='upload_csv'),
    path('preview_csv/', preview_csv, name='preview_csv'), 
]