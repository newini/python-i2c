from django.shortcuts import render

from .models import Data

def index(request):
    data_list = Data.objects.all()
    context = {
            'data_list': data_list
            }
    return render(request, 'index.html', context)
