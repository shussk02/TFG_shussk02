def map_dtype_to_field(data_type):
    if data_type == "int64":
        return "INT"
    elif data_type == "float64":
        return "DOUBLE"
    elif data_type == "bool":
        return "TINYINT(1)"
    elif data_type == "datetime64[ns]":
        return "DATETIME"
    else:
        return "VARCHAR(255)"