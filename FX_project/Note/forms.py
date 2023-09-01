from django import forms
from .models import ChartTable, DiaryTable, ReviewTable, PositionTable

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
    fields = ("name", "rule", "pair", "dt", "delta", "memo")
    # fields = ("name", "rule", "pair", "delta", "memo")
    widgets = {
      'name': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
      'memo': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
      'dt': forms.DateTimeInput(attrs={"type": "datetime-local"})
    }

class ReviewUpdateForm(forms.ModelForm):
  class Meta:
    model = ReviewTable
    # fields = ("name", "rule", "pair", "dt", "delta", "memo")
    fields = ("name", "rule", "pair", "delta", "memo")
    widgets = {
      'name': forms.Textarea(attrs={'rows': 1, 'cols': 50}),
      'memo': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
    }

class PositionSpeedForm(forms.ModelForm):
  now_datetime = forms.DateTimeField(widget=forms.HiddenInput())
  class Meta:
    model = PositionTable
    fields = ("quantity", "limit", "stop", "pair", "position_datetime")
    widgets = {
      'pair': forms.HiddenInput(),
      'position_datetime': forms.HiddenInput()
    }
    
class PositionMarketForm(forms.ModelForm):
  class Meta:
    model = PositionTable
    fields = ("condition", "limit", "stop","profit", "settlement_datetime", "settlement_rate")
  def __init__(self, *args, **kwargs):
    super(PositionMarketForm, self).__init__(*args, **kwargs)
    self.fields['limit'].initial = None
    self.fields['stop'].initial = None
    self.fields['condition'].initial = "market"
    for field_name in self.fields:
      self.fields[field_name].widget = forms.HiddenInput()

class PositionUpdateForm(forms.ModelForm):
  now_datetime = forms.DateTimeField(widget=forms.HiddenInput())
  class Meta:
    model = PositionTable
    fields = ("limit", "stop")


