from django.shortcuts import render

from .models import Data
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=+9), 'JST')


def index(request):
    data = Data.objects.filter(
            created_at__gte=datetime.now(JST)-timedelta(hours=1) # Get 12 hours before data
            ).order_by('-created_at')
    created_at_list = list( data.values_list('created_at', flat=True) )
    created_at_list = [ str(created_at) for created_at in created_at_list]
    temperature_list = list( data.values_list('temperature', flat=True) )
    humidity_list = list( data.values_list('humidity', flat=True) )
    eCO2_list = list( data.values_list('eCO2', flat=True) )
    TVOC_list = list( data.values_list('TVOC', flat=True) )
    context = {
            'created_at_list': created_at_list,
            'temperature_list': temperature_list,
            'humidity_list': humidity_list,
            'eCO2_list': eCO2_list,
            'TVOC_list': TVOC_list,
            }
    return render(request, 'index.html', context)
