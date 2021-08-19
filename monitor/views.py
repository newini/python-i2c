from django.shortcuts import render

from .models import Data

from django.views.generic import TemplateView
import plotly.offline as opy
import plotly.graph_objs as go


class Graph(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(Graph, self).get_context_data(**kwargs)

        x = list( Data.objects.order_by('-created_at').values_list('created_at', flat=True) )
        y = list( Data.objects.order_by('-created_at').values_list('temperature', flat=True) )

        trace1 = go.Scatter(x=x, y=y, marker={'color': 'red', 'symbol': 104, 'size': 10},
                            mode="lines",  name='1st Trace')

        data=go.Data([trace1])
        layout=go.Layout(title="Monitoring", xaxis={'title':'datetime'}, yaxis={'title':'temperature'})
        figure=go.Figure(data=data,layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        context['graph'] = div

        return context

def index(request):
    data_list = Data.objects.all()
    context = Graph().get_context_data()
    return render(request, 'index.html', context)
