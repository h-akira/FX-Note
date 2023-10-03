from django.urls import path, include
from .views import test, get_data
app_name = "test_app"
urlpatterns = [
  path('', test, name='test'),
  path('get_data/', get_data, name='get_data'),
]
