from django.shortcuts import render
from .models import HistoryTable

def history(request):
  histories = HistoryTable.objects.filter(user=request.user).order_by("-order_number","-order_datetime")
  # for h in histories:
    # print(h.__class__)
  header = [
    "アカウント",
    "注文番号",
    "取引種類",
    "通貨ペア",
    "売買",
    "注文タイプ",
    "取引数量",
    "状態",
    "失効理由",
    "注文日時",
    "注文レート",
    "執行条件",
    "約定日時",
    "約定レート",
    "決済損益",
    "累計スワップ"
  ]
  width = [
  100,
  80,
  100,
  100,
  50,
  100,
  80,
  100,
  80,
  200,
  200,
  200,
  200,
  200,
  200,
  200
  ]
  context = {"histories":histories, "header":header, "width":width}
  return render(request, 'Note/history.html', context)

def chart(request):
  context = None
  return render(request, 'Note/chart.html', context)
