# 基本
import sys
import os
import pandas as pd
import datetime
from pytz import timezone
import calendar
# django
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# modelsとforms
from .models import HistoryTable, ChartTable, HistoryLinkTable, DiaryTable
from .forms import ChartForm, DiaryForm
# 独自関数
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import lib.chart
import lib.chart_settings
# チャート出力用
import io
import base64
from matplotlib import use
use("Agg")
import mplfinance as mpf

# 曜日変換要
WEEK = ("月","火","水","木","金","土","日")

# html用
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
  histories_all = HistoryTable.objects.filter(user=request.user).order_by("-order_number","-order_datetime")
  # paginator = Paginator(histories_all, 50)
  per_page = request.GET.get('per_page', 50)
  paginator = Paginator(histories_all, per_page)
  page = request.GET.get('page')
  histories = paginator.get_page(page)
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
  _charts = ChartTable.objects.filter(user=request.user).order_by("-id")
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
def chart_image(request,id, _HttpResponse=True, _chart=None, histories=None):
  # 該当のchartのデータを取得
  if _chart == None:
    _chart = get_object_or_404(ChartTable, pk=id)
  # 該当のチャートと紐付けられている取引履歴を取得
  if histories == None:
    histories = [i.history for i in HistoryLinkTable.objects.filter(chart=_chart)]
    histories = sorted(histories, reverse=True, key=lambda x: x.id)
    histories = sorted(histories, reverse=True, key=lambda x: x.order_datetime)
  # 為替データを取得
  df = lib.chart.GMO_dir2DataFrame(
    os.path.join(os.path.dirname(__file__), "../data/rate"), 
    pair=_chart.pair,
    date_range=[
      (_chart.standard_datetime-datetime.timedelta(days=1)).date(),
      (_chart.standard_datetime+datetime.timedelta(days=1)).date()
    ]
  ) 
  # 足を変換
  df = lib.chart.resample(df, _chart.rule)
  # テクニカル指標を追加
  df = lib.chart_settings.add_technical_columns(df)
  # 最もstandard_datetimeに近い列の周辺のデータを取得する
  target_datetime = pd.Timestamp(_chart.standard_datetime)
  nearest_index = (pd.DataFrame(df.index) - target_datetime).abs().idxmin().date
  start_index = max(0, nearest_index - _chart.minus_delta)
  end_index = min(nearest_index + _chart.plus_delta, len(df) - 1)
  df = df.iloc[start_index:end_index+1]
  
  ### チャートを作成
  # 共通部分
  plot_args = lib.chart_settings.plot_args.copy()
  # テクニカル指標を追加
  plot_args =  lib.chart_settings.add_technical_lines(plot_args, df)
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
  plot_args["hlines"] = hlines
  # 取引期間
  # execution = [i.execution_datetime for i in histories if i.execution_datetime != None]
  # if len(execution) >= 2:
  #   transaction_start=pd.Timestamp(min(execution).astimezone(timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M"),tz=timezone("Asia/Tokyo"))
  #   transaction_end=pd.Timestamp(max(execution).astimezone(timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M"),tz=timezone("Asia/Tokyo"))
  #   dates_df = pd.DataFrame(df.index)
  #   where_values = pd.notnull(dates_df[(dates_df>=transaction_start)&(dates_df<=transaction_end)])['date'].values
  #   max_value = df["bb_up_3"].max(),
  #   min_value = df["bb_down_3"].min(),
  #   plot_args["fill_between"] = dict(y1=max_value, y2=min_value, where=where_values, alpha=0.3) 
  # 縦線
  vlines=dict(vlines=[],colors=[],linewidths=[])
  for history in histories:
    if history.execution_datetime != None and history.state != "canceled" and history.order_rate != None:
      vlines["vlines"].append(history.execution_datetime)
      if history.buy_sell == "buy":
        vlines["colors"].append("r")
      else:
        vlines["colors"].append("b")
      vlines["linewidths"].append(0.1)
  plot_args["vlines"] = vlines
  # 画像の大きさ
  plot_args["figsize"] = (19,8)
  # plot_args["figratio"] = (10,6)
  # 画像の出力先
  buf = io.BytesIO()
  plot_args["savefig"] = {'fname':buf,'dpi':100}
  # 出力
  mpf.plot(df, **plot_args)
  buf.seek(0)
  if _HttpResponse:
    return HttpResponse(buf, content_type='image/png')
  else:
    image_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return image_data
    # htmldjangoにおいて以下のように記述することで出力できる:
    # <img src="data:image/png;base64,{{ image_data  }}" alt="Chart">

@login_required
def chart_image_day(request, pair, year, month, day, _HttpResponse=True):
  pair = pair.replace("/","")
  dt = datetime.datetime(year, month, day)
  file = os.path.join(
    os.path.dirname(__file__), 
    "../data/rate", 
    pair,
    "{0}{1:02d}".format(year, month),
    "{0}_{1}{2:02d}{3:02d}.csv".format(pair, year, month, day)
  )
  if os.path.isfile(file):
    df = lib.chart.GMO_dir2DataFrame(
      os.path.join(os.path.dirname(__file__), "../data/rate"), 
      pair=pair,
      date_range=[
        (dt-datetime.timedelta(days=5)).date(), # 移動平均線等の計算のため，年末年始等にも対応して5日前から
        (dt+datetime.timedelta(days=1)).date()  # 未満のため+1
      ]
    ) 
    # 15分足
    df = lib.chart.resample(df, "15T")
    # テクニカル指標を追加
    df = lib.chart_settings.add_technical_columns(df)
    # 当日分
    df = df.iloc[-96:]
    ### チャートを作成
    # 共通部分
    plot_args = lib.chart_settings.plot_args.copy()
    # テクニカル指標を追加
    plot_args =  lib.chart_settings.add_technical_lines(plot_args, df)
    # 画像の大きさ
    plot_args["figsize"] = (10,6)
    # 画像の出力先
    buf = io.BytesIO()
    plot_args["savefig"] = {'fname':buf,'dpi':100}
    # タイトル
    # plot_args["title"] = f"{pair} 15T"
    # 出力
    mpf.plot(df, **plot_args)
    buf.seek(0)
    if _HttpResponse:
      return HttpResponse(buf, content_type='image/png')
    else:
      image_data = base64.b64encode(buf.getvalue()).decode("utf-8")
      return image_data
      # htmldjangoにおいて以下のように記述することで出力できる:
      # <img src="data:image/png;base64,{{ image_data  }}" alt="Chart">
  else:
    return None

@login_required
def chart_detail(request, id):
  # 該当のchartのデータを取得
  _chart = get_object_or_404(ChartTable, pk=id)
  # 該当のチャートと紐付けられている取引履歴を取得
  histories = [i.history for i in HistoryLinkTable.objects.filter(chart=_chart)]
  histories = sorted(histories, reverse=True, key=lambda x: x.id)
  histories = sorted(histories, reverse=True, key=lambda x: x.order_datetime)
  image_data = chart_image(request, id, _HttpResponse=False, _chart=_chart, histories=histories)
  ### 渡すもの
  context = {
    "id": id,
    "chart":_chart,
    "histories":histories, 
    "image_data":image_data,
    "header":history_header, 
    "width":history_width,
    "box":False, 
    "checked":False,
  }
  return render(request, 'Note/chart_detail.html', context)

@login_required
def histories2edit(request):
  histories = HistoryTable.objects.filter(
    id__in=request.POST.getlist("register")).order_by("-order_number","-order_datetime"
  )
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
    # "user":request.user,
    "pair":pairs[0],
    "standard_datetime": ave,
    "plus_delta":100,
    "minus_delta":100
  }
  form = ChartForm(initial=initial)
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
def none2edit(request):
  initial = {
    "plus_delta":100,
    "minus_delta":100
  }
  form = ChartForm(initial=initial)
  context = {
    "form":form,
    "table":False,
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
    # latest_chart = form.save()
    instance = form.save(commit=False)  # まだDBには保存しない
    instance.user = request.user  # ログインしているユーザー情報をセット
    instance.save()  # DBに保存
    if histories.exists():
      for history in histories:
        obj = HistoryLinkTable(chart=instance, history=history)
        obj.save()
    return chart_detail(request, instance.id)
    # return redirect("Note:chart")
  else:
    print("not valid")
    return redirect("Note:history")

@login_required
def chart_update(request,id):
  _chart = get_object_or_404(ChartTable, pk=id)
  form = ChartForm(request.POST, instance=_chart)
  if form.is_valid():
    form.save()
    return chart_detail(request, id) 
  else:
    return redirect("Note:chart",id)

@login_required
def chart_delete(request, id):
  _chart = get_object_or_404(ChartTable, pk=id)
  _chart.delete()
  return redirect("Note:chart_index")

@login_required
def calendar_index(request,year=None,month=None):
  if year == None and month == None:
    DIFF = 9
    dt = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF)
    return redirect("Note:calendar",dt.year,dt.month)
  # カレンダーを作成
  calendar.setfirstweekday(calendar.SUNDAY)
  _calendar = [row.split() for row in calendar.month(year,month).split("\n")]
  if _calendar[-1]==[]:
    _calendar.pop(-1)
  if len(_calendar[2])!=7:
    _calendar[2] = [""]*(7-len(_calendar[2]))+_calendar[2]
  if len(_calendar[-1])!=7:
    _calendar[-1] = _calendar[-1]+[""]*(7-len(_calendar[-1]))
  _calendar.pop(0)
  _calendar[0] = ["日","月","火","水","木","金","土"]
  # todayに色をつけたいので
  dt_now = datetime.datetime.now()
  if dt_now.year == year and dt_now.month == month:
    today = str(dt_now.day)
  else:
    today = None
  context = { 
      "year":year,
      "month":month,
      "calendar":_calendar,
      "today":today
  }
  if month!=12:
    context["next"]={"year":year, "month":month+1}
  else:
    context["next"]={"year":year+1, "month":1}
  if month!=1:
    context["prev"]={"year":year, "month":month-1}
  else:
    context["prev"]={"year":year-1, "month":12}
  return render(request,'Note/calendar.html',context)

@login_required
def diary(request, year, month, day, option=None):
  try:
    obj = DiaryTable.objects.get(date=datetime.date(year,month,day))
  except DiaryTable.DoesNotExist:
    obj = None
  image_USDJPY = chart_image_day(request, "USD/JPY", year, month, day, _HttpResponse=False)
  image_EURJPY = chart_image_day(request, "EUR/JPY", year, month, day, _HttpResponse=False)
  image_EURUSD = chart_image_day(request, "EUR/USD", year, month, day, _HttpResponse=False)
  context = {
    "year":year, 
    "month":month,
    "day":day,
    "weekday":WEEK[datetime.date(year,month,day).weekday()],
    "obj":obj,
    "image_USDJPY":image_USDJPY,
    "image_EURJPY":image_EURJPY,
    "image_EURUSD":image_EURUSD,
    "form":None,
    "type":None,
    "option":option
  }
  if option == "edit":
    if obj == None:
      form = DiaryForm()
      context["type"] = "add"
    else:
      form = DiaryForm(instance=obj)
      context["type"] = "update"
    context["form"] = form
  return render(request, 'Note/diary.html', context)

@login_required
def diary_create(request, year, month, day):
  if request.method == 'POST':
    form = DiaryForm(request.POST)
    if form.is_valid():
      instance = form.save(commit=False)  # まだDBには保存しない
      instance.date = datetime.date(year,month,day)  # 日付をセット
      instance.save()  # DBに保存
    return redirect("Note:diary",year,month,day)

@login_required
def diary_update(request, id):
  _diary = get_object_or_404(DiaryTable, pk=id)
  if request.method == 'POST':
    diaryForm = DiaryForm(request.POST, instance=_diary)
    if diaryForm.is_valid():
      diaryForm.save()
    year = _diary.date.year
    month = _diary.date.month 
    day = _diary.date.day
    return redirect("Note:diary", year, month, day)

@login_required
def diary_delete(request, id):
  _diary = get_object_or_404(DiaryTable, pk=id)
  year=_diary.date.year 
  month =_diary.date.month
  day =_diary.date.day
  _diary.delete()
  return redirect("Note:diary", year, month, day)

