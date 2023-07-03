#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created: 2023-05-23 02:02:40

# Import
import pandas as pd
import talib
import numpy
import glob
import os
import re
import io
import datetime
import matplotlib
from pytz import timezone
# matplotlib.use('TkAgg')
# matplotlib.use('Qt5Agg')
matplotlib.use("Agg")
# import matplotlib.pyplot as plt
import mplfinance as mpf

def GMO_dir2DataFrame(dir_name,pair="USDJPY",date_range=None):
  # pairは"/"を含んでいてもいなくても処理可能
  # date_rangeはdatetime.date型を要素に持つリストまたはタプル
  # ディレクトリ構造は以下の通り:
  # .
  # |-USDJPY
  # | |-202303
  # | | |-USDJPY_20230301.csv
  # | | |-USDJPY_20230302.csv
  # | | |-USDJPY_20230303.csv
  # | | |-...
  # | |-202304
  # | | |-...
  # | |-202305
  # |   |-...
  # |-EURJPY
  #    |-...
  file_list = glob.glob(os.path.join(dir_name,pair.replace("/",""))+f"/*/{pair.replace('/','')}_*.csv")
  df = pd.DataFrame()
  for file in file_list:
    if os.path.basename(file)[:len(pair.replace("/",""))] != pair.replace("/","") or file[-4:] != ".csv":
      print(f"skip: {file}")
      continue
    m = re.search(r"\d{4}\d{2}\d{2}", file)
    if m:
      file_date = datetime.datetime.strptime(m.group(),"%Y%m%d").date()  # 日付文字列を取得
    else:
      continue
    if date_range != None:
      if date_range[0] <= file_date < date_range[1]:
        pass
      else:
        continue
    df = pd.concat([df,GMO_csv2DataFrame(file)])
  df = df.sort_values(by="date", ascending=True)
  return df


def GMO_csv2DataFrame(file_name,BID_ASK="BID"):
  # GMOクリック証券からダウンロードしたヒストリカルデータ（CSVファイル）を読み込み，
  # mplfinanceで扱えるデータフレームにして返す．
  df = pd.read_csv(file_name, encoding='shift_jis').rename(
    columns={
      '日時':'date', 
      f'始値({BID_ASK})':'Open', 
      f'高値({BID_ASK})':'High', 
      f'安値({BID_ASK})':'Low', 
      f'終値({BID_ASK})':'Close'
    }
  )
  for col in df:
    if col not in ["Open", "High", "Low", "Close", "date"]:
      df = df.drop(col, axis=1) 
  df["date"] = pd.to_datetime(df["date"])
  df.set_index("date", inplace=True)
  df.index = df.index.tz_localize(timezone('Asia/Tokyo'))
  print(df)
  return df

def add_BBands(df,period=20,nbdev=2,matype=0, name={"up":"bb_up", "middle":"bb_middle", "down":"bb_down"}):
  # mplfinanceのデータフレームにボリンジャーバンドの列を追加する．
  bb_up, bb_middle, bb_down = talib.BBANDS(numpy.array(df['Close']), timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev, matype=matype)
  df[name['up']]=bb_up
  df[name['middle']]=bb_middle
  df[name['down']]=bb_down
  return df

def add_SMA(df, period, name):
  df[name]=talib.SMA(df["Close"], timeperiod=period)
  return df

def resample(df, rule):
  # 1分足からN分足など変換する
  # ruluは5Tなど
  # NaNの行は削除されてしまうので他の行を追加している場合は注意
  df_old = df.copy()
  df["Open"] = df_old["Open"].resample(rule).first()
  df["High"] = df_old["High"].resample(rule).max()
  df["Low"] = df_old["Low"].resample(rule).min()
  df["Close"] = df_old["Close"].resample(rule).last()
  df = df.dropna(how="any")
  return df

def gen_chart(df,transaction_start=None,transaction_end=None,max_value=None, min_value=None, hlines=None,vlines=None,lines=None, style=None, savefig=None,figsize=(2,1),png=False, dpi=200):
  # hlinesとvlinseは辞書型
  # 例: {'hlines':[136.28,136.32],'colors':['g','r'],'linewidths'=[1,1]}
  # linesは辞書型を要素とするリスト
  # 辞書型はmpf.make_addplotの引数
  # 第一引数であるDataFrameのkeyは"data"らしい
  # savefigも辞書型
  # 例: {'fname':'test.png','dpi':100}
  plot_args = {
    "type":"candle",
  }
  if transaction_start != None and transaction_end != None:
    # 型変換
    # print("*********************")
    # print(transaction_start)
    # print(transaction_end)
    # print("*********************")
    if transaction_start.__class__ == str:
      transaction_start=pd.Timestamp(transaction_start, tz=timezone("Asia/Tokyo"))
    elif transaction_start.__class__ == datetime.datetime:
      transaction_start=pd.Timestamp(transaction_start.astimezone(timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M"),tz=timezone("Asia/Tokyo"))
    if transaction_end.__class__ == str:
      transaction_end=pd.Timestamp(transaction_end,tz=timezone("Asia/Tokyo"))
    elif transaction_end.__class__ == datetime.datetime:
      transaction_end=pd.Timestamp(transaction_end.astimezone(timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M"),tz=timezone("Asia/Tokyo"))
      # transaction_end=pd.Timestamp(transaction_end.strftime("%Y-%m-%d %H:%M"), tz=timezone("Asia/Tokyo"))
    dates_df = pd.DataFrame(df.index)
    if max_value == None:
      max_value = df['Close'].max()
    if min_value == None:
      min_value = df['Low'].min()
    where_values = pd.notnull(dates_df[(dates_df>=transaction_start)&(dates_df<=transaction_end)])['date'].values
    plot_args["fill_between"] = dict(y1=max_value, y2=min_value, where=where_values, alpha=0.3) 
  if lines != None:
    plot_args["addplot"] = [mpf.make_addplot(**line_args) for line_args in lines]
  # if "bb_up" in df.columns and "bb_middle" in df.columns and "bb_down" in df.columns:
    # plot_args["addplot"] = [
      # mpf.make_addplot(df[['bb_up', 'bb_down']],linestyle='dashdot', color='r', alpha=0.5),
      # mpf.make_addplot(df['bb_middle'], color='b', alpha=0.5)
    # ]
  if style != None:
    plot_args["style"] = style
  if hlines != None:
    plot_args["hlines"] = hlines
  if vlines != None:
    plot_args["vlines"] = vlines
  if savefig != None:
    plot_args["figsize"] = figsize
    plot_args["savefig"] = savefig
  mpf.plot(df, **plot_args)

def test():
  import argparse
  parser = argparse.ArgumentParser(description="""\

""", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
  # parser.add_argument("-o", "--output", metavar="output-file", default="output", help="output file")
  # parser.add_argument("-l", "--little", action="store_true", help="little endian")
  parser.add_argument("file", metavar="input-file", help="input file")
  options = parser.parse_args()
  df = GMO_csv2DataFrame(options.file)
  df = resample(df, "5T")
  df = add_BBands(df,20,2,0)
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
  ]
  # chart.gen_chart(df.head(100),"2023-05-01 07:23","2023-05-01 07:33",dict(hlines=[136.28,136.32],colors=["g","r"]),figsize=(10,5),savefig=dict(fname="test.png",dpi=1000))
  gen_chart(df.head(100),"2023-05-01 07:23","2023-05-01 07:33",dict(hlines=[136.28,136.32],colors=["g","g"],linewidths=[0.1,0.1]),lines=lines)

if __name__ == '__main__':
  test()
