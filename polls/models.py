from django.db import models
from pandas import DataFrame

# Función para mapear tipos de datos de pandas a tipos de campos de Django
def map_dtype_to_field(data_type):
    if data_type == "int64":
        return models.IntegerField()
    elif data_type == "float64":
        return models.FloatField()
    elif data_type == "bool":
        return models.BooleanField()
    elif data_type == "datetime64[ns]":
        return models.DateTimeField()
    else:
        return models.CharField(max_length=255)

# Función para crear un modelo a partir de un DataFrame
def create_model_from_dataframe(df, model_name):
    class NewModel(models.Model):
        class Meta:
            db_table = model_name.lower()

    for column in df.columns:
        column_type = map_dtype_to_field(df[column].dtype)
        field_kwargs = {'max_length': 255} if isinstance(column_type, models.CharField) else {}
        setattr(NewModel, column, column_type(**field_kwargs))

    return NewModel