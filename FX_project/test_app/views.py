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
  df = lib.chart.resample(df, "15T")
  df = lib.chart.add_SMA(df, 20, "SMA_20").dropna() 
  data = []
  for index, row in df.iterrows():
    data.append(
      {
        # "time": index.tz_localize(None).isoformat(),
        "time": int(index.tz_localize(None).timestamp()),
        "open": row["Open"],
        "high": row["High"],
        "low": row["Low"],
        "close": row["Close"],
        "sma20": row["SMA_20"]
      }
    )
  return JsonResponse(data, safe=False)

def test(request):
  context = {}
  return render(request,'test_app/test.html',context)
