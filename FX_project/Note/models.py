from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

KIND = (("new","新規"),("settlement","決済"))
BUY_SELL = (("buy","買"),("sell","売"))
STATE = (("accepted","受付済"),("executed","約定済"),("canceled","取消済"))
# CONDITION = (("指値","limit"),("逆指値","stop"),("成行","market"))
CONDITION = (("limit","指値"),("stop","逆指値"),("market","成行"))
# RULE = (("1分足","1T"),("3分足","3T"),("15分足","15T"))
RULE = (
  ("1T","1分足"),
  ("3T","3分足"),
  ("5T","5分足"),
  ("15T","15分足"),
  ("30T","30分足"),
  ("1H","1時間足"),
  ("4H","4時間足"),
  ("D","日足"),
)
PAIR = (
  ("USD/JPY", "USD/JPY"),
  ("EUR/JPY","EUR/JPY"),
  ("EUR/USD","EUR/USD"),
  ("GBP/JPY","GBP/JPY")
)

class HistoryTable(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  account = models.CharField(max_length=50)
  order_number = models.IntegerField()
  pair = models.CharField(max_length=10)  # choicesは利用しない
  order_type  = models.CharField(max_length=20)
  kind = models.CharField(max_length=10, choices=KIND)
  buy_sell = models.CharField(max_length=10, choices=BUY_SELL)
  quantity = models.FloatField()
  state = models.CharField(max_length=10, choices=STATE)
  revocation_reason = models.CharField(max_length=10, null=True, blank=True)  # 失効理由(ほぼOCO)
  order_datetime = models.DateTimeField()
  order_rate = models.FloatField(null=True, blank=True)
  condition = models.CharField(max_length=10, choices=CONDITION)
  execution_datetime = models.DateTimeField(null=True, blank=True)
  execution_rate = models.FloatField(null=True, blank=True)
  unit = models.CharField(max_length=10,default="JPY")
  profit = models.FloatField(null=True, blank=True)
  swap = models.FloatField(null=True, blank=True)
  memo = models.CharField(max_length=511)
  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=["user", "account", "order_number"],
        name="history_unique"
      )
    ]
  
class ChartTable(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  name = models.CharField(max_length=255, default=timezone.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
  pair = models.CharField(max_length=10, choices=PAIR)
  rule = models.CharField(max_length=10, choices=RULE)
  standard_datetime = models.DateTimeField()
  minus_delta = models.IntegerField(default=100)
  plus_delta = models.IntegerField(default=100)
  memo = models.CharField(max_length=511,null=True, blank=True)

class HistoryLinkTable(models.Model):
  chart = models.ForeignKey(ChartTable, on_delete=models.CASCADE)
  history = models.ForeignKey(HistoryTable, on_delete=models.CASCADE)

class DiaryTable(models.Model):
  date = models.DateField(unique=True)
  text = models.CharField(max_length=2047,null=True, blank=True)


class ReviewTable(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  name = models.CharField(max_length=255, default=timezone.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
  # pair = models.CharField(max_length=10, choices=PAIR)
  rule = models.CharField(max_length=10, choices=RULE)
  delta = models.IntegerField(default=150)
  dt = models.DateTimeField()







