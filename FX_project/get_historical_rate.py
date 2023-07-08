#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created: 2023-06-11 14:11:03

# Import
import sys
import os
import numpy
import shutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from time import sleep
import datetime
import json

def parse_args():
  import argparse
  parser = argparse.ArgumentParser(description="""\

""", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
  parser.add_argument("--encoding", metavar="encoding", default="utf-8", help="encoding")
  parser.add_argument("--sleep", metavar="second", type=int, default=1, help="time interval")
  parser.add_argument("-y", "--year", metavar="year", type=int, help="year")
  parser.add_argument("-m", "--month", metavar="month", type=int, help="month")
  parser.add_argument("-o", "--output", metavar="directory", default="./data/rate", help="directory")
  parser.add_argument("-l", "--headless", action="store_true", help="hide browser")
  parser.add_argument("file", metavar="input-file", help="input file")
  options = parser.parse_args()
  if not options.year:
    options.year = datetime.datetime.now().year
  if not options.month:
    options.month = datetime.datetime.now().month
  options.output = os.path.abspath(options.output)
  return options

def main():
  # ArgumentParser
  options = parse_args()
  # 保存先の準備
  if os.path.exists(os.path.join(options.output, "temp")):
    shutil.rmtree(os.path.join(options.output, "temp"))
  os.makedirs(os.path.join(options.output,"temp"))
  # jsonを読む
  info = json.load(open(options.file, mode="r", encoding=options.encoding))
  if not info["selenium"]["password"]:
    info["selenium"]["password"] = input("Password: ")
  
  # seleniumの準備
  driver_options = Options()
  driver_options.add_experimental_option(
    'prefs',
    {
      "download.default_directory": os.path.join(options.output,"temp"),  # ダウンロード先のディレクトリ
      "download.prompt_for_download": False,  # ダウンロード時にダイアログを表示しない
      "download.directory_upgrade": True
    }
  )
  if options.headless:
    driver_options.add_argument('--headless')
  if "driver" not in info["selenium"].keys():
    driver = webdriver.Chrome(driver_options)
  elif not info["selenium"]["driver"]:
    driver = webdriver.Chrome(driver_options)
  else:
    driver = webdriver.Chrome(info["selenium"]["driver"], options=driver_options)
  # アクセス
  driver.get(info["selenium"]["url"]["login"])
  sleep(options.sleep)
  # ログイン
  driver.find_element(By.ID, "j_username").send_keys(info["selenium"]["username"])
  driver.find_element(By.ID, "j_password").send_keys(info["selenium"]["password"])
  sleep(options.sleep)
  driver.find_element(By.NAME, "LoginForm").click()
  sleep(options.sleep)
  # ダウンロード
  for u in info["selenium"]["url"]["data"].values():
    driver.get(u.format(options.year,"{0:02d}".format(options.month)))
    sleep(options.sleep)
  driver.quit()
  # 配置
  unzipped = "{0}{1:02d}".format(options.year, options.month)
  for zip_file in os.listdir(os.path.join(options.output, "temp")):
    subprocess.run(f"unzip {zip_file}", shell=True, cwd=os.path.join(options.output, "temp"))
    subprocess.run(f"rsync -av {unzipped} ../{zip_file[:6]}", shell=True, cwd=os.path.join(options.output, "temp"))
    subprocess.run(f"rm -r {unzipped}", shell=True, cwd=os.path.join(options.output, "temp"))
  # 一時ファイルを削除
  shutil.rmtree(os.path.join(options.output, "temp"))

if __name__ == '__main__':
  main()
