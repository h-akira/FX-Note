from django.urls import path
from .views import index 

app_name = 'Note'

urlpatterns = [
    path('history/',history, name='history'),
    path('trade/',history, name='history'),
]
