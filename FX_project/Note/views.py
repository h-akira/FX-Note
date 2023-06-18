import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from django.shortcuts import render, get_object_or_404
from .models import HistoryTable, ChartTable, HistoryLinkTable
from .forms import ChartForm
from django.http import HttpResponse
from django.db.models import Avg
# import tempfile
import lib.chart as cha
import matplotlib.pyplot as plt
import io
import base64
import datetime
import pandas as pd

def history(request):
  histories = HistoryTable.objects.filter(user=request.user).order_by("-order_number","-order_datetime")
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
    "スワップ",
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

def chart_index(request):
  charts = ChartTable.objects.filter(user=request.user)
  links = [HistoryLinkTable.objects.filter(chart=i).count() for i in charts]
  header = [
    "登録名",
    "通貨ペア",
    "足",
    "基準日時",
    "新規+決済",
    "操作"
  ]
  width = [
  200,  # 登録名
  100,  # 通貨ペア
  50,  # 足
  200,  # 基準日時
  100,  # 新規+決済
  100  # 操作
  ]
  context = {"charts":charts, "links":links, "header":header, "width":width}
  return render(request, 'Note/chart_index.html', context)

def chart(request,id):
  _chart = get_object_or_404(ChartTable, pk=id)
  _link = get_object_or_404(HistoryLinkTable, pk=1)
  df = cha.GMO_dir2DataFrame(
    os.path.join(os.path.dirname(__file__), "../data/rate"), 
    pair=_chart.pair,
    date_range=[
      (_chart.standard_datetime-datetime.timedelta(days=1)).date(),
      (_chart.standard_datetime+datetime.timedelta(days=1)).date()
    ]
  ) 
  df = cha.add_BBands(df,20,2,0)
  # 最もstandard_datetimeに近い列の周辺のデータを取得する
  target_datetime = pd.Timestamp(_chart.standard_datetime).tz_localize(None)
  nearest_index = (pd.DataFrame(df.index) - target_datetime).abs().idxmin().date
  start_index = max(0, nearest_index - _chart.minus_delta)
  end_index = min(nearest_index + _chart.plus_delta, len(df) - 1)
  df = df.iloc[start_index:end_index+1]
  # 画像の出力先
  buf = io.BytesIO()
  # チャートを作成
  cha.gen_chart(
    df,
    # "2023-05-01 07:23",
    # "2023-05-01 07:33",
    # hlines=dict(hlines=[136.28,136.6],colors=["g","g"],linewidths=[0.1,0.1]),
    lines=[
      {
        "data":df[["bb_up","bb_down"]],
        "linestyle":"dashdot",
        "color":"r",
        "alpha":0.5
      },
      {
        "data":df[["bb_middle"]],
        "color":"b",
        "alpha":0.5
      }
    ],
    savefig={'fname':buf,'dpi':100},
    figsize=(10,5)
  )
  # png = buf.getvalue()
  image_data = base64.b64encode(buf.getvalue()).decode("utf-8")
  return render(request, 'Note/chart.html', {'chart_data': image_data})
  # buf.close()

def histories2chart(request):
  # print(request.POST.getlist("register"))
  histories = HistoryTable.objects.filter(id__in=request.POST.getlist("register")).order_by("-order_number","-order_datetime")
  # dts = histories.values_list("execution_datetime"))
  dts = [i[0].timestamp() for i in histories.values_list("execution_datetime") if i[0] != None]
  if len(dts) == 0:
    dts = [i[0].timestamp() for i in histories.values_list("order_datetime") if i[0] != None]
  timezones = [i[0].tzinfo for i in histories.values_list("execution_datetime") if i[0] != None]
  if len(timezones) != timezones.count(timezones[0]):
    raise Exception
  ave = datetime.datetime.fromtimestamp(sum(dts)/len(dts),tz=timezones[0])
  print(dts)
  print(timezones)
  print(ave)
  initial = {
    "user":request.user,
    "standard_datetime": ave,
    "plus_delta":50,
    "minus_delta":50
  }
  form = ChartForm(initial=initial)
  # print(request.POST.getlist["register"])
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
    "スワップ",
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
  context = {"histories":histories, "header":header, "width":width, "form":form}
  return render(request, 'Note/edit.html', context)







