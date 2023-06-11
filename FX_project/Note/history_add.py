#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created: 2023-06-11 14:11:03

# Import
import sys
import os
import numpy
import pandas as pd
import lib.history as his
from models import HistoryTable
# import models.HistoryTable
import django

def parse_args():
  import argparse
  parser = argparse.ArgumentParser(description="""\

""", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
  parser.add_argument("-o", "--output", metavar="output-file", default="output", help="output file")
  parser.add_argument("-l", "--little", action="store_true", help="little endian")
  parser.add_argument("files", metavar="input-file", nargs="*", help="input file")
  options = parser.parse_args()
  return options

def main():
  # ArgumentParser
  options = parse_args()
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FX_project.settings")
  django.setup()
  print("hogehoge")
  df = None
  for file in options.files:
    if not df:
      df = his.GMO_html2df(open(file, mode="r").read())
    df = his.add_data(df, his.GMO_html2df(open(file, mode="r").read()))
  for d in df:
    print(d["pair"])

  # obj = HistoryTable(**)

if __name__ == '__main__':
  main()
