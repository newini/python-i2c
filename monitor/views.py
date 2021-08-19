from django.shortcuts import render

from .models import Data

from django.views.generic import TemplateView
import plotly.offline as opy
import plotly.graph_objs as go


class Graph(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(Graph, self).get_context_data(**kwargs)

        context['temperature_graph'] = self.get_graph_div('temperature', 'Temperature', 'Temperature [C]')
        context['humidity_graph'] = self.get_graph_div('humidity', 'Humidity', 'Relative humidity [%]')
        context['eCO2_graph'] = self.get_graph_div('eCO2', 'eCO2', 'eCO2 [ppm]')
        context['TVOC_graph'] = self.get_graph_div('TVOC', 'TVOC', 'TVOC [ppb]')

        return context

    def get_graph_div(self, column_name, title, y_axis_name):
        x = list( Data.objects.order_by('-created_at').values_list('created_at', flat=True) )
        y = list( Data.objects.order_by('-created_at').values_list(column_name, flat=True) )
        trace1 = go.Scatter(x=x, y=y, marker={'color': 'blue', 'symbol': 104, 'size': 10},
                            mode="lines", name='3rd Trace')

        data = go.Data([trace1])
        layout = go.Layout(title=title, xaxis={'title': 'datetime'}, yaxis={'title': y_axis_name},
                template='plotly_dark')
        figure = go.Figure(data=data,layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        return div


def index(request):
    data_list = Data.objects.all()
    context = Graph().get_context_data()
    return render(request, 'index.html', context)
