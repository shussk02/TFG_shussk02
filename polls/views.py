import csv
import io
from django.views.generic.list import ListView
from pyexpat.errors import *
from django.http import HttpResponse
from django.shortcuts import redirect, render
import pandas as pd
from .forms import UploadFileForm

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def mostrar_csv(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_csv = request.FILES['archivo_csv']
            separador = form.cleaned_data['separador']
            try:
                df = pd.read_csv(archivo_csv, sep=separador)
                tabla_html = df.to_html()
            except pd.errors.EmptyDataError:
                tabla_html = "<p>El archivo CSV está vacío.</p>"
            except pd.errors.ParserError:
                tabla_html = "<p>El archivo no es un CSV válido.</p>"
            return render(request, 'mostrar_csv.html', {'form': form, 'tabla_html': tabla_html})
    else:
        form = UploadFileForm()
    return render(request, 'cargar_csv.html', {'form': form})