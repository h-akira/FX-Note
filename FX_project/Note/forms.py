from django import forms
from .models import ChartTable, DiaryTable, ReviewTable

class ChartForm(forms.ModelForm):
  class Meta:
    model = ChartTable
    # fields = ("user", 'name', 'pair', 'rule',"standard_datetime", "minus_delta", "plus_delta", "memo")
    fields = ('name', 'pair', 'rule',"standard_datetime", "minus_delta", "plus_delta", "memo")
    widgets = {
      'memo': forms.Textarea(attrs={'rows': 10, 'cols': 50}),
      'standard_datetime': forms.DateTimeInput(attrs={"type": "datetime-local"})
    }
class DiaryForm(forms.ModelForm):
  class Meta:
    model = DiaryTable
    fields = ("text",)
    widgets = {
      'text': forms.Textarea(attrs={'rows': 10, 'cols': 50})
    }
class ReviewForm(forms.ModelForm):
  class Meta:
    model = ReviewTable
    fields = ("name", "rule", "dt", "delta")
    widgets = {
      'standard_datetime': forms.DateTimeInput(attrs={"type": "datetime-local"})
    }
