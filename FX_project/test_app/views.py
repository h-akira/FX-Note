import os
import sys
import datetime
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
# 独自関数
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import lib.chart
import lib.chart_settings

def get_data(request):
  df = lib.chart.GMO_dir2DataFrame(
    os.path.join(os.path.dirname(__file__), "../data/rate"), 
    pair="USD/JPY",
    date_range=[
      (datetime.datetime.now()-datetime.timedelta(days=5)).date(),
      (datetime.datetime.now()-datetime.timedelta(days=3)).date()
    ]
  ) 
  df = lib.chart.resample(df, "5T")
  df = lib.chart.add_BBands(
    df,20,2,0,name={"up":"bb_up_2", "middle":"bb_middle", "down":"bb_down_2"}
  )
  df = lib.chart.add_BBands(
    df,20,3,0,name={"up":"bb_up_3", "middle":"bb_middle", "down":"bb_down_3"}
  )
  df = lib.chart.add_SMA(df, 5, "SMA_05")
  df = lib.chart.add_SMA(df, 20, "SMA_20") 
  df = lib.chart.add_SMA(df, 60, "SMA_60")
  df = df.dropna() 
  data = []
  for index, row in df.iterrows():
    data.append(
      {
        "time": int(index.tz_localize(None).timestamp()),
        "open": row["Open"],
        "high": row["High"],
        "low": row["Low"],
        "close": row["Close"],
        "sma05": row["SMA_05"],
        "sma20": row["SMA_20"],
        "sma60": row["SMA_60"],
        "bb_up_2": row["bb_up_2"],
        "bb_up_3": row["bb_up_3"],
        "bb_down_2": row["bb_down_2"],
        "bb_down_3": row["bb_down_3"]
      }
    )
  return JsonResponse(data, safe=False)

def test(request):
  context = {}
  return render(request,'test_app/test.html',context)
