import io
from django.views.generic.list import ListView
from pyexpat.errors import *
from django.http import HttpResponse
from django.shortcuts import redirect, render
import pandas as pd
import datetime
from django.contrib import messages
from .forms import UploadFileForm
#from .utils import *

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

                # Obtener las columnas de tipo datetime
                datetime_columns = [col for col, dtype in df.dtypes.items() if dtype == 'datetime64[ns]']

                if datetime_columns:
                    df[datetime_columns] = df[datetime_columns].astype(str)
                    # Guardar las columnas datetime en una sesión separada
                    datetime_columns_dict = {col: df[col].astype(str).tolist() for col in datetime_columns}
                    request.session['datetime_columns'] = datetime_columns_dict

                else:
                    request.session['datetime_columns'].clear()

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
        
    
        # Obtener las columnas datetime de la sesión secundaria
        datetime_columns_dict = request.session.get('datetime_columns', {})
        
        for col, values in datetime_columns_dict.items():
            if col in df.columns:
                # Convertir los valores a datetime si la columna existe en el DataFrame
                df[col] = pd.to_datetime(df[col])
            else:
            # Si la columna no existe, la agregamos al DataFrame y luego convertimos los valores a datetime
                pass

        # Saco los nombres de las columnas y los datos de la tabla
        datos = df.values.tolist()
        columnas = df.columns.tolist()

        # Obtener tipos de datos de cada columna
        tipos_de_dato = df.dtypes
        
        # Zipear columnas y tipos_de_dato
        columnas_con_tipos = zip(columnas, tipos_de_dato)

        # Se renderiza la plantilla 'vista_previa_csv.html' con los datos del DataFrame
        return render(request, 'vista_previa_csv.html', {'columnas_con_tipos': columnas_con_tipos, 'datos': datos})
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
        

        # Obtener las columnas datetime de la sesión secundaria
        datetime_columns_dict = request.session.get('datetime_columns', {})

        for col, values in datetime_columns_dict.items():
            if col in df.columns:
                # Convertir los valores a datetime si la columna existe en el DataFrame
                df[col] = pd.to_datetime(df[col])
            else:
                pass
        
        # Saco los nombres de las columnas y los datos de la tabla
        columnas = df.columns.tolist()
        datos = df.values.tolist()

        # Obtener tipos de datos de cada columna
        tipos_de_dato = df.dtypes
        # Zipear columnas y tipos_de_dato
        columnas_con_tipos = zip(columnas, tipos_de_dato)

        # Se renderiza la plantilla 'vista_modificable_csv.html' con los datos del DataFrame
        return render(request, 'vista_modificable_csv.html', {'columnas_con_tipos': columnas_con_tipos, 'datos': datos})
    else:
        # Si no hay un DataFrame en la sesión, se redirige al usuario a la vista 'cargar_csv'
        return redirect('cargar_csv')


def update(request):
    if request.method == 'POST':
        # Obtener los nuevos nombres de las columnas y tipos de datos del formulario
        columnas_actualizadas = [request.POST[f'header_{i}'] for i in range(len(request.POST)) if f'header_{i}' in request.POST]
        tipos_actualizados = [request.POST[f'tipo_{i}'] for i in range(len(request.POST)) if f'tipo_{i}' in request.POST]

        
        # Obtener los datos originales del DataFrame de la sesión
        df_dict = request.session.get('df')

        if df_dict is not None:

            # Crear un DataFrame con los datos originales
            df = pd.DataFrame(df_dict)


            try:
                
                df.columns = columnas_actualizadas

                # Convertir los tipos de datos a los tipos de pandas correspondientes
                df = convertir_tipos_de_dato(df, tipos_actualizados)

                
                # Obtener las columnas de tipo datetime
                datetime_columns = [col for col, dtype in df.dtypes.items() if dtype == 'datetime64[ns]']

                if datetime_columns:
                    df[datetime_columns] = df[datetime_columns].astype(str)
                    # Guardar las columnas datetime en una sesión separada
                    datetime_columns_dict = {col: df[col].astype(str).tolist() for col in datetime_columns}
                    request.session['datetime_columns'] = datetime_columns_dict

                else:
                    request.session['datetime_columns'].clear()

                
                # Guardar el DataFrame actualizado en la sesión
                request.session['df'] = df.to_dict(orient='records')

                # Redirigir de vuelta a la vista mostrar_csv para mostrar los cambios
                return redirect('mostrar_csv')
            
            except Exception as e:
                # Si hay un error al modificar el tipo de datos, mostrar una alerta al usuario
                messages.error(request, f"No se pudo modificar al tipo de datos: {str(e)}")
                # Redirigir de vuelta a la vista modificar_csv para que el usuario pueda corregir
                return redirect('modificar_csv')
    
    # Si no es una solicitud POST, redirigir a la página de inicio o mostrar un mensaje de error
    return redirect('cargar_csv')


def convertir_tipos_de_dato(df, tipos):

    for columna, tipo_nuevo in zip(df.columns, tipos):
        tipo_anterior = df[columna].dtype
        
        if tipo_anterior == tipo_nuevo:
            continue  # El tipo de dato ya es el mismo, no se necesita conversión
        
        elif tipo_nuevo == 'bool':
            if tipo_anterior == 'int64':
                # Verifica si todos los valores son 0s o 1s
                if set(df[columna].unique()) == {0, 1}:
                    # Convierte la columna en tipo booleano
                    df[columna] = df[columna].astype(tipo_nuevo)
                else:
                    return Exception
            elif tipo_anterior == 'object':
                # Verifica si todos los valores son true o false
                if set(df[columna].unique()) == {'True', 'False'}:
                    # Convierte la columna en tipo booleano
                    df[columna] = df[columna].astype(tipo_nuevo)
                else:
                    return Exception
            else:
                return Exception

        elif tipo_nuevo == 'object':
            df[columna] = df[columna].astype(str)
        elif tipo_nuevo == 'int64':
            # Convertir a tipo 'Int64' si no hay pérdida de datos
            if pd.to_numeric(df[columna], errors='coerce').notnull().all():
                df[columna] = pd.to_numeric(df[columna], errors='coerce').astype(tipo_nuevo)
            else:
                return Exception
        elif tipo_nuevo == 'float64':
            # Convertir a tipo 'float' si no hay pérdida de datos
            if pd.to_numeric(df[columna], errors='coerce').notnull().all():
                df[columna] = pd.to_numeric(df[columna], errors='coerce').astype(tipo_nuevo)
            else:
                return Exception
        elif tipo_nuevo == 'datetime64':
            if tipo_anterior == 'object':
                
                df[columna] = pd.to_datetime(df[columna])
            else:
                return Exception
    return df


def columnas_seleccionadas(request):
    if request.method == 'POST':

        # Obtener los nombres de las columnas seleccionadas

        selected = [request.POST[key] for key in request.POST.keys() if key.startswith('columna')]

        if (selected):


            # Obtener los datos originales del DataFrame de la sesión
            df_dict = request.session.get('df')

            if df_dict is not None:

                # Crear un DataFrame con los datos originales
                df = pd.DataFrame(df_dict)

                # Filtramos el dataframe con los nombres de las columnas obtenidas
                df_filtrado = df[selected]

                # Convertir el DataFrame filtrado a un nuevo diccionario
                df_filtrado_dict = df_filtrado.to_dict(orient='records')

                # Guardar el nuevo diccionario en la sesión con una clave diferente
                request.session['df_selected'] = df_filtrado_dict

                
                datetime_columns_dict = request.session.get('datetime_columns', {})

                for col, values in datetime_columns_dict.items():
                    if col in df_filtrado.columns:
                        # Convertir los valores a datetime si la columna existe en el DataFrame
                        df_filtrado[col] = pd.to_datetime(df_filtrado[col])
                        df[col] = pd.to_datetime(df[col])
                    else:
                        pass

                # Saco los nombres de las columnas y los datos correspondientes a estas
                columnas = df_filtrado.columns.tolist()
                datos = df_filtrado.values.tolist()

                #Modelo_df = crear_modelo_desde_dataframe(df)
                # Obtener tipos de datos de cada columna
                tipos_de_dato = df_filtrado.dtypes

                # Zipear columnas y tipos_de_dato
                columnas_con_tipos = zip(columnas, tipos_de_dato)

            return render(request, 'selected_columns_view.html', {'columnas_con_tipos': columnas_con_tipos, 'datos': datos})

        else:
            return redirect('mostrar_csv')