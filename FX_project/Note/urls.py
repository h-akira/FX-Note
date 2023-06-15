from django.urls import path
from .views import history, chart ,fig

app_name = 'Note'

urlpatterns = [
    path('history/',history, name='history'),
    path('chart/',chart, name='chart'),
    # path('chart/fig',fig, name='fig'),
    # path('chart/<int:id>',chart, name='chart'),
    # path('chart/<int:id>/fig',fig, name='fig'),
]
