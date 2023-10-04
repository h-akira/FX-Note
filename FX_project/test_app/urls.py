from django.urls import path, include
from .views import test, get_data, get_vlines, get_hlines, get_periods
app_name = "test_app"
urlpatterns = [
  path('', test, name='test'),
  path('get_data/', get_data, name='get_data'),
  path('get_vlines/', get_vlines, name='get_vlines'),
  path('get_hlines/', get_hlines, name='get_hlines'),
  path('get_periods/', get_periods, name='get_periods'),
]
