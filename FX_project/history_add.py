#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created: 2023-06-11 14:11:03

# Import
import sys
import os
import numpy
import pandas as pd
from pytz import timezone
import lib.history as his
import django

def parse_args():
  import argparse
  parser = argparse.ArgumentParser(description="""\

""", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
  parser.add_argument("-u", "--username", metavar="username", default="admin", help="username")
  parser.add_argument("-a", "--account", metavar="account", default="DEMO", help="account")
  parser.add_argument("-t", "--timezone", metavar="timezone", default="Asia/Tokyo", help="timezone")
  parser.add_argument("-o", "--output", metavar="output-file", default="output", help="output file")
  # parser.add_argument("-l", "--little", action="store_true", help="little endian")
  parser.add_argument("files", metavar="input-file", nargs="*", help="input file")
  options = parser.parse_args()
  return options

def jp2en(d):
  dic = {
    "成行":"market",
    "通常":"normal",
    "OCO":"OCO",
    "新規":"new",
    "決済":"settlement",
    "買":"buy",
    "売":"sell",
    "取消済":"canceled",
    "受付済":"accepted",
    "約定済":"executed",
    "指値":"limit",
    "逆指値":"stop"
  }
  d["order_type"] = dic[d["order_type"]]
  d["kind"] = dic[d["kind"]]
  d["buy_sell"] = dic[d["buy_sell"]]
  d["state"] = dic[d["state"]]
  d["condition"] = dic[d["condition"]]
  try:
    d["revocation_reason"] = dic[d["revocation_reason"]]
  except KeyError:
    pass
  return d

def main():
  # ArgumentParser
  options = parse_args()
  # タイムゾーン
  tz = timezone(options.timezone)
  # 必要な設定
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FX_project.settings")
  django.setup()
  from django.contrib.auth.models import User
  from Note.models import HistoryTable
  # userを取得
  user = User.objects.get(username=options.username)
  # HTMLを解析してpd.DataFrameを得る
  df = None
  for file in options.files:
    if not df:
      df = his.GMO_html2df(open(file, mode="r").read())
    df = his.add_data(df, his.GMO_html2df(open(file, mode="r").read()))
  # 引数とするため辞書型にする
  dict_list = [row.to_dict() for index, row in df.iterrows()]
  # 諸々の処理の後Tableに追加
  for d in dict_list:
    # 設定
    d["state"] = d["state and revocation reason"].split()[0]
    if len(d["state and revocation reason"].split()) > 1:
      d["revocation_reason"] = d["state and revocation reason"].split()[-1]
    d.pop("state and revocation reason")
    # 欠損を取り除く
    for key in list(d.keys()):
      if d[key].__class__ == pd._libs.missing.NAType or d[key].__class__ == pd._libs.tslibs.nattype.NaTType:
        d.pop(key)
    # DateTime型の変換
    if "order_datetime" in d.keys():
      d["order_datetime"] = tz.localize(d["order_datetime"].to_pydatetime())
    if "execution_datetime" in d.keys():
      d["execution_datetime"] = tz.localize(d["execution_datetime"].to_pydatetime())
    # 追加
    d["user"] = user
    d["account"] = options.account
    # 日本語を英語に変換
    d = jp2en(d)
    # テーブルに追加
    obj = HistoryTable(**d)
    obj.save()

if __name__ == '__main__':
  main()
