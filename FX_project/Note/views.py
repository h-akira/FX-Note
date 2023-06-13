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
    "スワップ"
  ]
  width = [
  100,  # アカウント
  80,  # 注文番号
  100,  # 取引種類
  100,  # 通貨ペア
  50,  # 売買
  100,  # 注文タイプ
  80,  # 取引数量
  100,  # 状態
  80,  # 失効理由
  200,  # 注文日時
  100,  # 注文レート
  80,  # 執行条件
  200,  # 約定日時
  100,  # 約定レート
  100,  # 決済損益
  100  # スワップ
  ]
  context = {"histories":histories, "header":header, "width":width}
  return render(request, 'Note/history.html', context)

def chart(request):
  context = None
  return render(request, 'Note/chart.html', context)
