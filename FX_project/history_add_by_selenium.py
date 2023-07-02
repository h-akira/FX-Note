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
from lib.language import Dictionary
import django
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from time import sleep
import datetime
import json

def parse_args():
  import argparse
  parser = argparse.ArgumentParser(description="""\

""", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
  parser.add_argument("--encoding", metavar="encoding", default="utf-8", help="encoding")
  parser.add_argument("--sleep", metavar="second", type=int, default=1, help="encoding")
  parser.add_argument("-d", "--demo", action="store_true", help="demo trade")
  parser.add_argument("-l", "--headless", action="store_true", help="hide browser")
  parser.add_argument("file", metavar="input-file", help="input file")
  options = parser.parse_args()
  return options

def jp2en(d):
  dic = Dictionary.JP2EN
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

def add(html,user,account,tz,HistoryTable):
  # すでに登録済みのデータがあったかを知らせる変数
  done = False
  # HTMLを解析してpd.DataFrameを得る
  df = his.GMO_html2df(html)
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
    d["account"] = account
    # 日本語を英語に変換
    d = jp2en(d)
    # テーブルに追加
    obj = HistoryTable(**d)
    try:
      obj.save()
    except django.db.utils.IntegrityError:
      done=True
  return done

def main():
  # ArgumentParser
  options = parse_args()
  # jsonを読む
  info = json.load(open(options.file, mode="r", encoding=options.encoding))
  if not info["selenium"]["password"]:
    info["selenium"]["password"] = input("Password: ")
  
  # データベースに追加するための設定
  # タイムゾーン
  tz = timezone(info["django"]["timezone"])
  # 必要な設定
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FX_project.settings")
  django.setup()
  from django.contrib.auth.models import User
  from Note.models import HistoryTable
  # userを取得
  user = User.objects.get(username=info["django"]["username"])
  
  # seleniumの準備
  driver_options = Options()
  if options.headless:
    options.add_argument('--headless')
  driver = webdriver.Chrome(info["selenium"]["driver"], options=driver_options)
  # アクセス
  driver.get(info["selenium"]["url"])
  sleep(options.sleep)
  # ログイン
  driver.find_element_by_id("j_username").send_keys(info["selenium"]["username"])
  driver.find_element_by_id("j_password").send_keys(info["selenium"]["password"])
  sleep(options.sleep)
  driver.find_element_by_name("LoginForm").click()
  sleep(options.sleep)
  # デモでない場合は全体のページからFXのページに移動
  if not options.demo:
    driver.find_element_by_id("fxneoMenu").find_element_by_tag_name("a").click()
    sleep(options.sleep)
  # 「注文・取引一覧」
  driver.find_element_by_name("orderHistory").find_element_by_tag_name("a").click()
  sleep(options.sleep)
  # 表示件数を200件にする
  dropdown = driver.find_element_by_id('row-limit-selection')
  select = Select(dropdown)
  select.select_by_index(2)
  driver.find_element_by_id("search-button").find_element_by_tag_name("a").click()
  sleep(options.sleep)

  # データベースに追加
  while True:
    done = add(driver.page_source, user=user, account=info["django"]["account"], tz=tz, HistoryTable=HistoryTable)
    if done:
      break
    span_elements = driver.find_elements_by_tag_name('span')
    for span_element in span_elements:
      if span_element.text == ">":
        span_element.click()
        sleep(options.sleep)
        break
    else:
      break
    sleep(5)
  driver.quit()

if __name__ == '__main__':
  main()
