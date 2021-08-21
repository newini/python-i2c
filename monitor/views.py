from django.shortcuts import render

from .models import Data


def index(request):
    created_at_list = list( Data.objects.order_by('-created_at').values_list('created_at', flat=True) )
    created_at_list = [ str(created_at) for created_at in created_at_list]
    temperature_list = list( Data.objects.order_by('-created_at').values_list('temperature', flat=True) )
    humidity_list = list( Data.objects.order_by('-created_at').values_list('humidity', flat=True) )
    eCO2_list = list( Data.objects.order_by('-created_at').values_list('eCO2', flat=True) )
    TVOC_list = list( Data.objects.order_by('-created_at').values_list('TVOC', flat=True) )
    context = {
            'created_at_list': created_at_list,
            'temperature_list': temperature_list,
            'humidity_list': humidity_list,
            'eCO2_list': eCO2_list,
            'TVOC_list': TVOC_list,
            }
    return render(request, 'index.html', context)
