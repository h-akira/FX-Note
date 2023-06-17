from django.contrib import admin
from .models import HistoryTable, ChartTable, HistoryLinkTable

admin.site.register(HistoryTable)
admin.site.register(ChartTable)
admin.site.register(HistoryLinkTable)
