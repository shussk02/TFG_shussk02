from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path("", views.index, name="index"),
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('preview_csv/', preview_csv, name='preview_csv'),
    path('confirm_csv/', confirm_csv, name='confirm_csv'),  
]