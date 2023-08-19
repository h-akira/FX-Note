from django import forms
from .models import ChartTable

class ChartForm(forms.ModelForm):
  class Meta:
    model = ChartTable
    fields = ("user", 'name', 'pair', 'rule',"standard_datetime", "minus_delta", "plus_delta", "memo")
    widgets = {
      'memo': forms.Textarea(attrs={'rows': 10, 'cols': 50}),
    }
