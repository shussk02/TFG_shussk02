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
    # Verificar si la solicitud es de tipo POST
    if request.method == 'POST':
        # Crear un formulario de carga de archivo con los datos recibidos
        form = UploadFileForm(request.POST, request.FILES)
        
        # Verificar si el formulario es válido
        if form.is_valid():

            # Obtener el archivo CSV y el separador del formulario válido
            archivo_csv = request.FILES['archivo_csv']
            separador = form.cleaned_data['separador']
            
            try:
                # Leo el archivo CSV usando pandas
                df = pd.read_csv(archivo_csv, sep=separador)
                
                # Convierto el DataFrame en una lista de diccionarios
                df_dict = df.to_dict(orient='records')

                # Guardo la lista de diccionarios en la sesión
                request.session['df'] = df_dict
                
                # Se redirige al usuario a la vista 'modificar_csv' para mostrar los datos del CSV
                return redirect('mostrar_csv')
            
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                # Se capturan errores que surjan al procesar el archivo CSV
                form.add_error('archivo_csv', 'Error al procesar el archivo CSV.')
    
    # Si la solicitud no es de tipo POST, se crea un formulario vacío
    else:
        form = UploadFileForm()
    
    # Se renderiza el template 'cargar_csv.html' con el formulario
    return render(request, 'cargar_csv.html', {'form': form})


def mostrar_csv(request):

    # Obtengo el DataFrame almacenado en la sesión del usuario
    df_dict = request.session.get('df')
    
    # Se verifica si hay un DataFrame almacenado en la sesión
    if df_dict is not None:

        # Convierto la lista de diccionarios en un DataFrame
        df = pd.DataFrame(df_dict)
        
        # Saco los nombres de las columnas y los datos de la tabla
        columnas = df.columns.tolist()
        datos = df.values.tolist()

        # Se renderiza la plantilla 'vista_modificable_csv.html' con los datos del DataFrame
        return render(request, 'vista_previa_csv.html', {'columnas': columnas, 'datos': datos})
    else:
        # Si no hay un DataFrame en la sesión, se redirige al usuario a la vista 'cargar_csv'
        return redirect('cargar_csv')



# Vista para modificar el archivo CSV cargado
def modificar_csv(request):

    # Obtengo el DataFrame almacenado en la sesión del usuario
    df_dict = request.session.get('df')
    
    # Se verifica si hay un DataFrame almacenado en la sesión
    if df_dict is not None:

        # Convierto la lista de diccionarios en un DataFrame
        df = pd.DataFrame(df_dict)
        
        # Saco los nombres de las columnas y los datos de la tabla
        columnas = df.columns.tolist()
        datos = df.values.tolist()

        # Se renderiza la plantilla 'vista_modificable_csv.html' con los datos del DataFrame
        return render(request, 'vista_modificable_csv.html', {'columnas': columnas, 'datos': datos})
    else:
        # Si no hay un DataFrame en la sesión, se redirige al usuario a la vista 'cargar_csv'
        return redirect('cargar_csv')


def update(request):
    if request.method == 'POST':

        # Obtener los nuevos nombres de las columnas del formulario
        columnas_actualizadas = [request.POST[f'header_{i}'] for i in range(len(request.POST)) if f'header_{i}' in request.POST]

        # Obtener los datos originales del DataFrame de la sesión
        df_dict = request.session.get('df')

        if df_dict is not None:
            # Crear un DataFrame con los datos originales
            df = pd.DataFrame(df_dict)

            # Renombrar las columnas con los nuevos nombres
            df.columns = columnas_actualizadas

            # Guardar el DataFrame actualizado en la sesión
            request.session['df'] = df.to_dict(orient='records')

        # Redirigir de vuelta a la vista modificar_csv para mostrar los cambios
        return redirect('mostrar_csv')
    
    else:
        # Si no es una solicitud POST, redirigir a la página de inicio o mostrar un mensaje de error
        return redirect('cargar_csv')
