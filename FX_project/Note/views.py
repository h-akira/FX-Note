import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
import lib.chart as cha
import matplotlib.pyplot as plt
import io
import base64
import datetime
import pandas as pd
from pytz import timezone
from .models import HistoryTable, ChartTable, HistoryLinkTable
from .forms import ChartForm

history_header = [
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
history_width = [
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

@login_required
def history(request):
  histories = HistoryTable.objects.filter(user=request.user).order_by("-order_number","-order_datetime")
  context = {
    "histories":histories, 
    "header":history_header, 
    "width":history_width,
    "box":True, 
    "checked":False
  }
  return render(request, 'Note/history.html', context)

@login_required
def chart_index(request):
  _charts = ChartTable.objects.filter(user=request.user)
  links = [HistoryLinkTable.objects.filter(chart=i).count() for i in _charts]
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
  context = {"charts":_charts, "links":links, "header":header, "width":width, "box":False, "checked":False}
  return render(request, 'Note/chart_index.html', context)

@login_required
def chart(request,id):
  _chart = get_object_or_404(ChartTable, pk=id)
  histories = [i.history for i in HistoryLinkTable.objects.filter(chart=_chart)]
  histories = sorted(histories, reverse=True, key=lambda x: x.id)
  histories = sorted(histories, reverse=True, key=lambda x: x.order_datetime)
  execution = [i.execution_datetime for i in histories if i.execution_datetime != None]
  if len(execution) >= 2:
    start = min(execution)
    end = max(execution)
  else:
    start = None
    end = None
  # _link = get_object_or_404(HistoryLinkTable, pk=1)
  df = cha.GMO_dir2DataFrame(
    os.path.join(os.path.dirname(__file__), "../data/rate"), 
    pair=_chart.pair,
    date_range=[
      (_chart.standard_datetime-datetime.timedelta(days=1)).date(),
      (_chart.standard_datetime+datetime.timedelta(days=1)).date()
    ]
  ) 
  # 足を変換
  df = cha.resample(df, _chart.rule)
  # ボリンジャーバンドを追加
  df = cha.add_BBands(df,20,2,0,name={"up":"bb_up_2", "middle":"bb_middle", "down":"bb_down_2"})
  df = cha.add_BBands(df,20,3,0,name={"up":"bb_up_3", "middle":"bb_middle", "down":"bb_down_3"})
  # 移動平均線を追加
  df = cha.add_SMA(df, 5, "SMA_5") 
  df = cha.add_SMA(df, 20, "SMA_20") 
  df = cha.add_SMA(df, 50, "SMA_50") 
  print(df)
  # 最もstandard_datetimeに近い列の周辺のデータを取得する
  target_datetime = pd.Timestamp(_chart.standard_datetime)
  nearest_index = (pd.DataFrame(df.index) - target_datetime).abs().idxmin().date
  start_index = max(0, nearest_index - _chart.minus_delta)
  end_index = min(nearest_index + _chart.plus_delta, len(df) - 1)
  df = df.iloc[start_index:end_index+1]
  # 横線
  hlines=dict(hlines=[],colors=[],linewidths=[])
  for history in histories:
    if history.order_rate != None:
      hlines["hlines"].append(history.order_rate)
      if history.buy_sell == "buy":
        hlines["colors"].append("r")
      else:
        hlines["colors"].append("b")
      hlines["linewidths"].append(0.1)
  # 画像の出力先
  buf = io.BytesIO()
  # チャートを作成
  cha.gen_chart(
    df,
    transaction_start=start,
    transaction_end=end,
    max_value = df["bb_up_3"].max(),
    min_value = df["bb_down_3"].min(),
    hlines=hlines,
    lines=[
      {
        "data":df[["bb_up_2","bb_down_2"]],
        "linestyle":"dashdot",
        "color":"#aa4c8f",
        "alpha":1
      },
      {
        "data":df[["bb_up_3","bb_down_3"]],
        "linestyle":"dashdot",
        "color":"#96514d",
        "alpha":1
      },
      {
        "data":df[["SMA_50"]],
        "color":"y",
        "alpha":1
      },
      {
        "data":df[["SMA_20"]],
        "color":"#3eb370",
        "alpha":1
      },
      {
        "data":df[["SMA_5"]],
        "color":"#bc763c",
        "alpha":1
      }
    ],
    savefig={'fname':buf,'dpi':100},
    figsize=(18,8),
    # style="binance"
    style="nightclouds"
  )
  image_data = base64.b64encode(buf.getvalue()).decode("utf-8")
  # 渡すもの
  context = {
    "id": id,
    "image_data": image_data,
    "histories":histories, 
    "header":history_header, 
    "width":history_width,
    "box":False, 
    "checked":False,
  }
  return render(request, 'Note/chart.html', context)

@login_required
def histories2edit(request):
  # print(request.POST.getlist("register"))
  histories = HistoryTable.objects.filter(id__in=request.POST.getlist("register")).order_by("-order_number","-order_datetime")
  # dts = histories.values_list("execution_datetime"))
  dts = [i[0].timestamp() for i in histories.values_list("execution_datetime") if i[0] != None]
  if len(dts) == 0:
    dts = [i[0].timestamp() for i in histories.values_list("order_datetime") if i[0] != None]
  timezones = [i[0].tzinfo for i in histories.values_list("execution_datetime") if i[0] != None]
  if len(timezones) != timezones.count(timezones[0]):
    raise Exception
  pairs = [i[0] for i in histories.values_list("pair")]
  print(pairs)
  if len(pairs) != pairs.count(pairs[0]):
    raise Exception
  ave = datetime.datetime.fromtimestamp(sum(dts)/len(dts),tz=timezones[0])
  initial = {
    "user":request.user,
    "pair":pairs[0],
    "standard_datetime": ave,
    "plus_delta":100,
    "minus_delta":100
  }
  form = ChartForm(initial=initial)
  # print(request.POST.getlist["register"])
  context = {
    "histories":histories,
    "header":history_header,
    "width":history_width,
    "form":form,
    "table":True,
    "box":True, 
    "checked":True,
    "type":"add"
  }
  return render(request, 'Note/edit.html', context)

@login_required
def chart_edit(request, id):
  _chart = get_object_or_404(ChartTable, pk=id)
  form = ChartForm(instance=_chart)
  context = {
    "id":id,
    "form":form,
    "table":False,
    "box":False, 
    "checked":False,
    "type":"update"
  }
  return render(request, 'Note/edit.html', context)

@login_required
def chart_add(request):
  form = ChartForm(request.POST)
  histories = HistoryTable.objects.filter(id__in=request.POST.getlist("register"))
  print(histories)
  if form.is_valid():
    latest_chart = form.save()
    for history in histories:
      obj = HistoryLinkTable(chart=latest_chart, history=history)
      obj.save()
    return chart_index(request)
    # return index(request)
    # return redirect("Note:chart")
  else:
    print("not valid")
    return redirect("Note:history")

@login_required
def chart_update(request,id):
  _chart = get_object_or_404(ChartTable, pk=id)
  form = ChartForm(request.POST, instance=_chart)
  # form = ChartForm(request.POST, instance=article)
  if form.is_valid():
    form.save()
    return chart(request, id) 
  else:
    return redirect("Note:chart",id)

@login_required
def chart_delete(request, id):
  _chart = get_object_or_404(ChartTable, pk=id)
  _chart.delete()
  return redirect("Note:chart_index")


