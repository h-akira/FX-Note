from django.urls import path
from .views import history, chart ,chart_index, histories2edit, chart_add

app_name = 'Note'

urlpatterns = [
    path('history/',history, name='history'),
    path('chart/',chart_index, name='chart_index'),
    path('chart/generate/',histories2edit, name='chart_generate'),
    path('chart/add/',chart_add, name='chart_add'),
    path('chart/<int:id>',chart, name='chart'),
    # path('chart/<int:id>/fig',fig, name='fig'),
]
