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


# Vista para procesar la carga del archivo CSV
def cargar_csv(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_csv = request.FILES['archivo_csv']
            separador = form.cleaned_data['separador']
            try:
                df = pd.read_csv(archivo_csv, sep=separador)
                # Convertir el DataFrame en una lista de diccionarios
                df_dict = df.to_dict(orient='records')
                # Guardar la lista de diccionarios en la sesión
                request.session['df'] = df_dict
                return redirect('mostrar_csv')
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                form.add_error('archivo_csv', 'Error al procesar el archivo CSV.')
    else:
        form = UploadFileForm()
    return render(request, 'cargar_csv.html', {'form': form})

# Vista para mostrar el archivo CSV cargado
def mostrar_csv(request):
    df_dict = request.session.get('df')
    if df_dict is not None:
        # Convertir la lista de diccionarios en un DataFrame
        df = pd.DataFrame(df_dict)
        # Obtener los nombres de las columnas y los datos de la tabla
        columnas = df.columns.tolist()
        datos = df.values.tolist()
        # Combinar los nombres de las columnas y los datos en una lista
        tabla_html = [columnas] + datos
        return render(request, 'mostrar_csv.html', {'tabla_html': tabla_html})
    else:
        return redirect('cargar_csv')