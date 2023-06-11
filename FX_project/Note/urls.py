from django.urls import path
from .views import history, chart 

app_name = 'Note'

urlpatterns = [
    path('history/',history, name='history'),
    path('chart/',chart, name='chart'),
]
