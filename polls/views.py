import csv
import io
from logging import Logger
from django.forms import ValidationError
from django.views.generic.list import ListView
from pyexpat.errors import *
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import *
from .models import *

logger = Logger(__name__)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def upload_csv(request):
    template_name = "upload.html"
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a csv file')
        else:
            data_set = csv_file.read().decode('UTF-8')
            lines = data_set.split("\n")
            csv_data = []
            for line in lines:
                fields = line.split(";")
                if len(fields) < 4:
                    continue
                csv_data.append(fields)
            request.session['csv_data'] = csv_data
            return redirect('preview_csv')
    return render(request, template_name)


def preview_csv(request):
    csv_data = request.session.get('csv_data')
    if csv_data is None:
        return redirect('upload_csv')
    return render(request, 'preview.html', {'csv_data': csv_data})