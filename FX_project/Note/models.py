from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

KIND = (("new","新規"),("settlement","決済"))
BUY_SELL = (("buy","買"),("sell","売"))
STATE = (("accepted","受付済"),("executed","約定済"),("canceled","取消済"))
CONDITION = (("指値","limit"),("逆指値","stop"),("成行","market"))

class HistoryTable(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  account = models.CharField(max_length=50)
  order_number = models.IntegerField()
  pair = models.CharField(max_length=10)
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
  name = models.CharField(max_length=255)
  pair = models.CharField(max_length=10)
  rule = models.CharField(max_length=10)
  standard_datetime = models.DateTimeField()
  minus_delta = models.IntegerField(default=50)
  plus_delta = models.IntegerField(default=50)
  memo = models.CharField(max_length=511)







