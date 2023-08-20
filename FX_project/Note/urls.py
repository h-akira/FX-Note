from django.urls import path
from .views import history, chart_detail ,chart_index, histories2edit, chart_add, chart_edit, chart_update, chart_delete, chart_image, none2edit

app_name = 'Note'

urlpatterns = [
    path('history/',history, name='history'),
    path('chart/index/',chart_index, name='chart_index'),
    path('chart/generate/',histories2edit, name='chart_generate'),
    path('chart/create/',none2edit, name='chart_create'),
    path('chart/add/',chart_add, name='chart_add'),
    path('chart/edit/<int:id>',chart_edit, name='chart_edit'),
    path('chart/update/<int:id>',chart_update, name='chart_update'),
    path('chart/delete/<int:id>',chart_delete, name='chart_delete'),
    path('chart/detail/<int:id>',chart_detail, name='chart_detail'),
    path('chart/image/<int:id>',chart_image, name='chart_image'),
    # path('chart/<int:id>/fig',fig, name='fig'),
]
