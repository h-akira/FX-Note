from django.urls import path
from .views import history, chart ,chart_index

app_name = 'Note'

urlpatterns = [
    path('history/',history, name='history'),
    path('chart/',chart_index, name='chart_index'),
    path('chart/<int:id>',chart, name='chart'),
    # path('chart/<int:id>/fig',fig, name='fig'),
]
