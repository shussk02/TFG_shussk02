from django import forms

class UploadFileForm(forms.Form):
    archivo_csv = forms.FileField(label='Selecciona un archivo CSV')
    separador = forms.ChoiceField(choices=[(',', 'Coma'), (';', 'Punto y coma'), ('\t', 'Tabulación')], label='Selecciona el separador', initial=',')
