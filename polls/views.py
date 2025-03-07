from django.conf import settings
from django.views.generic.list import ListView
from pyexpat.errors import *
from django.http import HttpResponse
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from .forms import UploadFileForm
from .utils import *
from django.db import connections, transaction
from django.core.management import call_command
from django.apps import apps
from django.db.utils import OperationalError
import numpy as np
from django.contrib.auth.decorators import login_required

# Valores únicos disponibles para host, puerto y usuario
hosts = [
    {'name': 'max_host', 'port': 4007, 'user': 'maxuser'},
    {'name': 'mariadb1_host', 'port': 3306, 'user': 'root'},
    {'name': 'mariadb2_host', 'port': 3306, 'user': 'root'},
    {'name': 'mariadb3_host', 'port': 3306, 'user': 'root'},
]

@login_required
def cargar_csv(request):
    # Verificar si la solicitud es de tipo POST
    if request.method == 'POST':
        # Crear un formulario de carga de archivo con los datos recibidos
        form = UploadFileForm(request.POST, request.FILES)
        
        # Verificar si el formulario es válido
        if form.is_valid():
            archivo_csv = request.FILES['archivo_csv']
            separador = form.cleaned_data['separador']
            
            try:
                df = pd.read_csv(archivo_csv, sep=separador)

                # Obtener las columnas de tipo datetime
                datetime_columns = [col for col, dtype in df.dtypes.items() if dtype == 'datetime64[ns]']

                if datetime_columns:
                    df[datetime_columns] = df[datetime_columns].astype(str)
                    datetime_columns_dict = {col: df[col].astype(str).tolist() for col in datetime_columns}
                    request.session['datetime_columns'] = datetime_columns_dict
                else:
                    if 'datetime_columns' in request.session:
                        request.session['datetime_columns'].clear()

                df_dict = df.to_dict(orient='records')
                request.session['df'] = df_dict
                
                return redirect('polls:mostrar_csv')
            
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                form.add_error('archivo_csv', 'Error al procesar el archivo CSV.')
    
    else:
        form = UploadFileForm()
    
    
    
    # Obtener valores únicos
    unique_hosts = sorted({host['name'] for host in hosts})
    unique_ports = sorted({host['port'] for host in hosts})
    unique_users = sorted({host['user'] for host in hosts})

    # Valores preseleccionados (obtenemos del POST o valores predeterminados si no se envió nada)
    selected_host = request.POST.get('host', settings.DATABASES['default']['HOST'] if unique_hosts else "")
    selected_puerto = request.POST.get('puerto', settings.DATABASES['default']['PORT'] if unique_ports else "")
    selected_usuario = request.POST.get('usuario', settings.DATABASES['default']['USER'] if unique_users else "")

    context = {
        'form': form,
        'host': settings.DATABASES['default']['HOST'],
        'puerto': settings.DATABASES['default']['PORT'],
        'user': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD'],
        'unique_hosts': unique_hosts,
        'unique_ports': unique_ports,
        'unique_users': unique_users,
        'selected_host': selected_host,
        'selected_puerto': selected_puerto,
        'selected_usuario': selected_usuario
    }
    
    return render(request, 'cargar_csv.html', context)



def cambiarhp(request):
    if request.method == 'POST':
        # Obtener los nuevos valores de host, puerto, usuario y contraseña
        nuevo_host = request.POST.get('host')
        nuevo_puerto = request.POST.get('puerto')
        nuevo_usuario = request.POST.get('usuario')
        nueva_contrasena = request.POST.get('password')

        # Comprobar si los campos tienen valores
        if not (nuevo_host and nuevo_puerto and nuevo_usuario and nueva_contrasena):
            messages.error(request, "Debe proporcionar el host, puerto, usuario y contraseña.")
            return redirect('polls:cargar_csv')
        

        # Verificar si los valores proporcionados coinciden con los del arreglo
        es_valido = any(
            nuevo_host == h['name'] and int(nuevo_puerto) == h['port'] and nuevo_usuario == h['user']
            for h in hosts
        )

        if not es_valido:
            messages.error(request, "Los valores proporcionados no coinciden con los servidores disponibles.")
            return redirect('polls:cargar_csv')

        try:
            # Actualizar los parámetros de configuración de la base de datos en Django
            settings.DATABASES['default']['HOST'] = nuevo_host
            settings.DATABASES['default']['PORT'] = nuevo_puerto
            settings.DATABASES['default']['USER'] = nuevo_usuario
            settings.DATABASES['default']['PASSWORD'] = nueva_contrasena

            # Intentar realizar una consulta simple para verificar la conexión
            with connections['default'].cursor() as cursor:
                cursor.execute('SELECT 1')

            # Si la consulta es exitosa, se realiza el cambio
            messages.success(request, "Host, puerto, usuario y contraseña actualizados exitosamente.")
        except OperationalError as e:
            # Si hay un error de conexión, se muestra un mensaje de error
            messages.error(request, f"Error al intentar conectar con la base de datos: {str(e)}")
        except Exception as ex:
            messages.error(request, f"Ocurrió un error inesperado: {str(ex)}")

        return redirect('polls:cargar_csv')

    return render(request, 'cargar_csv.html')


    
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
                df[col] = pd.to_datetime(df[col], errors='coerce')
            else:
            # Si la columna no existe, la agregamos al DataFrame y luego convertimos los valores a datetime
                pass

        df = df.where(pd.notnull(df), None)

        # Saco los nombres de las columnas y los datos de la tabla
        datos = df.values.tolist()
        columnas = df.columns.tolist()

        # Obtener tipos de datos de cada columna
        tipos_de_dato = df.dtypes
        
        # Zipear columnas y tipos_de_dato
        columnas_con_tipos = zip(columnas, tipos_de_dato)

        messages.success(request, 'Archivo cargado correctamente.')
        # Se renderiza la plantilla 'vista_previa_csv.html' con los datos del DataFrame
        return render(request, 'vista_previa_csv.html', {'columnas_con_tipos': columnas_con_tipos, 'datos': datos})
    
    else:
        # Si no hay un DataFrame en la sesión, se redirige al usuario a la vista 'cargar_csv'
        return redirect('polls:cargar_csv')


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
                df[col] = pd.to_datetime(df[col], errors='coerce')
            else:
                pass
        
        df = df.where(pd.notnull(df), None)
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
        return redirect('polls:cargar_csv')


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
                    if 'datetime_columns' in request.session:
                        request.session['datetime_columns'].clear()

                
                # Guardar el DataFrame actualizado en la sesión
                request.session['df'] = df.to_dict(orient='records')

                # Redirigir de vuelta a la vista mostrar_csv para mostrar los cambios
                return redirect('polls:mostrar_csv')
            
            except Exception as e:
                # Si hay un error al modificar el tipo de datos, mostrar una alerta al usuario
                messages.error(request, f"No se pudo modificar al tipo de datos: {str(e)}")
                # Redirigir de vuelta a la vista modificar_csv para que el usuario pueda corregir
                return redirect('polls:modificar_csv')
    
    # Si no es una solicitud POST, redirigir a la página de inicio o mostrar un mensaje de error
    return redirect('polls:cargar_csv')


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

                
                # Obtener tipos de datos de cada columna
                tipos_de_dato = df_filtrado.dtypes



                # Zipear columnas y tipos_de_dato
                columnas_con_tipos = zip(columnas, tipos_de_dato)

                tablas = obtener_tablas_disponibles()
            return render(request, 'selected_columns_view.html', {'columnas_con_tipos': columnas_con_tipos, 'datos': datos, 'tablas': tablas})

        else:
    
            return redirect('polls:mostrar_csv')
    else:

        df_dict = request.session.get('df_selected')

        if df_dict is not None:

            # Crear un DataFrame con los datos originales
            df = pd.DataFrame(df_dict)
            
            datetime_columns_dict = request.session.get('datetime_columns', {})

            for col, values in datetime_columns_dict.items():
                if col in df.columns:
                    # Convertir los valores a datetime si la columna existe en el DataFrame
                    df[col] = pd.to_datetime(df[col])
                else:
                    pass

            # Saco los nombres de las columnas y los datos correspondientes a estas
            columnas = df.columns.tolist()
            datos = df.values.tolist()

            
            # Obtener tipos de datos de cada columna
            tipos_de_dato = df.dtypes
            
            # Zipear columnas y tipos_de_dato
            columnas_con_tipos = zip(columnas, tipos_de_dato)

            tablas = obtener_tablas_disponibles()
        return render(request, 'selected_columns_view.html', {'columnas_con_tipos': columnas_con_tipos, 'datos': datos, 'tablas': tablas})


def obtener_tablas_disponibles():
    with connections['default'].cursor() as cursor:
        # Ejecutar la consulta para obtener todas las tablas en la base de datos
        cursor.execute("SHOW TABLES LIKE 'app_%'")
        
        # Obtener los resultados de la consulta
        resultados = cursor.fetchall()
        
        # Extraer los nombres de las tablas de los resultados
        tablas = [fila[0] for fila in resultados]
        
    return tablas

def nueva_tabla(request):

    if request.method == 'POST':
        # Obtener el nombre de la tabla del formulario
        nombre_tabla = "app_" + request.POST.get('nombre_tabla')

        df_dict = request.session.get('df_selected')

        if df_dict is not None:

                # Crear un DataFrame con los datos originales
            df = pd.DataFrame(df_dict)

            datetime_columns_dict = request.session.get('datetime_columns', {})

            for col, values in datetime_columns_dict.items():
                if col in df.columns:
                    # Convertir los valores a datetime si la columna existe en el DataFrame
                    df[col] = pd.to_datetime(df[col])
                else:
                    pass

            # Convertir a minúsculas para usarlo como nombre de tabla en la base de datos
            table_name = nombre_tabla.lower()

            # Obtener una lista de nombres de tablas en la base de datos
            existing_tables = obtener_tablas_disponibles()


            # Verificar si la tabla ya existe en la base de datos
            if table_name not in existing_tables:
                # Si la tabla no existe, crearla utilizando SQL
                with connections['default'].cursor() as cursor:

                    # Define la sentencia SQL para crear la tabla
                    sql_columns = ",\n".join([f"{column} {map_dtype_to_field(df.dtypes[column])}" for column in df.columns])
                    sql_statement = f"""
                        CREATE TABLE {table_name} (
                            {sql_columns}
                        )
                    """
                    # Ejecuta la sentencia SQL
                    cursor.execute(sql_statement)
                # Después de crear la tabla, redirige a alguna página o realiza alguna acción
                return redirect('polls:columnas_seleccionadas')

                # Si la tabla ya existe, redirige a alguna página o realiza alguna acción
            return redirect('polls:columnas_seleccionadas')

            # Si la tabla ya existe, redirigir a alguna página o realizar alguna acción
        return redirect('polls:columnas_seleccionadas')


def insertar_datos(request):
    if request.method == 'POST':
        # Obtener el nombre de la tabla del formulario
        nombre_tabla = request.POST.get('tabla')
        df_dict = request.session.get('df_selected')

        if df_dict is not None:
            # Crear un DataFrame con los datos originales
            df = pd.DataFrame(df_dict)

            # Manejar columnas datetime
            datetime_columns_dict = request.session.get('datetime_columns', {})
            for col, values in datetime_columns_dict.items():
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce').apply(lambda x: None if pd.isna(x) else x)

            # Obtener columnas existentes en la tabla
            existing_columns_info = obtener_columnas_tabla(nombre_tabla)
            existing_columns = {col[0]: col[1] for col in existing_columns_info}

            # Validar columnas y tipos de datos
            for col in df.columns:
                if col not in existing_columns:
                    messages.error(request, f"La columna '{col}' del DataFrame no existe en la tabla de la base de datos.")
                    return redirect('polls:columnas_seleccionadas')
                elif not tipo_datos_coinciden(df[col].dtype, existing_columns[col]):
                    messages.error(request, f"El tipo de datos de la columna '{col}' no coincide con la tabla.")
                    return redirect('polls:columnas_seleccionadas')

            # Reemplazar valores NaT, NaN con None
            df = df.replace({pd.NaT: None, pd.NA: None, np.nan: None})

            # Crear la consulta SQL
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            sql = f"INSERT INTO {nombre_tabla} ({columns}) VALUES ({placeholders})"
            values = [tuple(row) for row in df.to_numpy()]

            # Usar una transacción atómica
            try:
                with transaction.atomic():
                    with connections['default'].cursor() as cursor:
                        cursor.executemany(sql, values)
                messages.success(request, f"Datos insertados correctamente en la tabla {nombre_tabla}.")
            except Exception as e:
                error_value = None
                for i, row in enumerate(values):
                    try:
                        with connections['default'].cursor() as cursor:
                            cursor.execute(sql, row)
                    except Exception as row_error:
                        error_value = row
                        break
                
                if error_value:
                    messages.error(request, f"Error al insertar datos. Detalles: {e}. Fila con error: {error_value}")
                else:
                    messages.error(request, f"Error al insertar datos en la tabla {nombre_tabla}. Detalles: {e}")
                return redirect('polls:columnas_seleccionadas')

            return redirect('polls:columnas_seleccionadas')

    return redirect('polls:columnas_seleccionadas')



def obtener_columnas_tabla(nombre_tabla):
    """
    Obtener las columnas existentes en una tabla de la base de datos junto con su tipo de datos.
    """
    with connections['default'].cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM {nombre_tabla}")
        columnas_info = cursor.fetchall()
        columnas = [(fila[0], fila[1]) for fila in columnas_info]
    return columnas

def tipo_datos_coinciden(dtype_pandas, tipo_mariadb):
    if dtype_pandas == 'int64':
        return tipo_mariadb.startswith('int')
    elif dtype_pandas == 'float64':
        return tipo_mariadb.startswith('double')
    elif dtype_pandas == 'datetime64[ns]':
        return tipo_mariadb.startswith('datetime')
    elif dtype_pandas == 'bool':
        return tipo_mariadb.startswith('tinyint')
    elif dtype_pandas == 'object':
        return tipo_mariadb.startswith('varchar')
    else:
        return False


