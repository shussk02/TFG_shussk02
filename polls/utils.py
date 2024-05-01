from dynamic_django_models import ModelBuilder
from django.db import models

def crear_modelo_desde_dataframe(df):
    # Inicializar el constructor del modelo
    builder = ModelBuilder()

    # Recorrer las columnas del DataFrame
    for columna, tipo in df.dtypes.items():
        # Convertir el tipo de pandas al equivalente de Django
        if tipo == 'object':
            tipo_django = models.CharField(max_length=100)  # Ajusta la longitud según tus necesidades
        elif tipo == 'int64':
            tipo_django = models.IntegerField()
        elif tipo == 'float64':
            tipo_django = models.FloatField()
        elif tipo == 'datetime64[ns]':
            tipo_django = models.DateTimeField()
        elif tipo == 'bool':
            tipo_django = models.BooleanField()
        else:
            # Maneja otros tipos de datos según sea necesario
            tipo_django = models.CharField(max_length=100)

        # Agregar el campo al constructor del modelo
        builder.add_field(columna, tipo_django)

    # Construir el modelo
    TuModeloDinamico = builder.build_model('Modelo_df')

    # Devolver el modelo dinámico creado
    return TuModeloDinamico
