from django.shortcuts import render

def history(request):
  context = None
  return render(request, 'Note/history.html', context)

def chart(request):
  context = None
  return render(request, 'Note/chart.html', context)
