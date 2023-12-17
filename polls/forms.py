from django import forms
from .models import *

class DataForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = "__all__"