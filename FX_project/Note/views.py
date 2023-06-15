from django.shortcuts import render, get_object_or_404
from .models import HistoryTable, ChartTable
from django.http import HttpResponse
import sys
import os
import tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import lib.chart as cha
import matplotlib.pyplot as plt
import io
import base64

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

def fig(request):

  ##########################################################################################
  # df = cha.GMO_csv2DataFrame(os.path.join(os.path.dirname(__file__), "../data/rate/USDJPY/202305/USDJPY_20230501.csv"))
  # df = cha.resample(df.head(500), "5T")
  # df = cha.add_BBands(df,20,2,0)
  # buf = io.BytesIO()
  # cha.gen_chart(
  #   df.head(500),
  #   "2023-05-01 07:23",
  #   "2023-05-01 07:33",
  #   dict(hlines=[136.28,136.6],colors=["g","g"],linewidths=[0.1,0.1]),
  #   lines=[
  #     {
  #       "data":df[["bb_up","bb_down"]],
  #       "linestyle":"dashdot",
  #       "color":"r",
  #       "alpha":0.5
  #     },
  #     {
  #       "data":df[["bb_middle"]],
  #       "color":"b",
  #       "alpha":0.5
  #     }
  #   ],
  #   savefig={'fname':buf,'dpi':100},
  #   figsize=(10,5)
  # )
  # png = buf.getvalue()
  # buf.close()
  # response = HttpResponse(png, content_type='image/png')
  ##########################################################################################
  return response

# def chart(request,id):
def chart(request):
  df = cha.GMO_csv2DataFrame(os.path.join(os.path.dirname(__file__), "../data/rate/USDJPY/202305/USDJPY_20230501.csv"))
  df = cha.resample(df.head(500), "5T")
  df = cha.add_BBands(df,20,2,0)
  buf = io.BytesIO()
  cha.gen_chart(
    df.head(500),
    "2023-05-01 07:23",
    "2023-05-01 07:33",
    dict(hlines=[136.28,136.6],colors=["g","g"],linewidths=[0.1,0.1]),
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
  # response = HttpResponse(png, content_type='image/png')
  #########################################################################################
  # _chart = get_object_or_404(ChartTable, pk=id)
  # context = {}
  
  # return render(request, 'Note/chart.html', context)
