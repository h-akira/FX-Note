from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

KIND = (("new","新規"),("settlement","決済"))
BUY_SELL = (("buy","買"),("sell","売"))
STATE = (("accepted","受付済"),("done","約定済"),("cancel","取消済"))

class HistoryTable(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  account = models.CharField(max_length=50)
  order_numver = models.IntegerField()
  pair = models.CharField(max_length=10)
  trade_type  = models.CharField(max_length=20)
  kind = models.CharField(max_length=10, choices=KIND)
  buy_sell = models.CharField(max_length=10, choices=BUY_SELL)
  quantity = models.FloatField()
  state = models.CharField(max_length=10, choices=STATE)
  order_datetime = models.DateTimeField()
  order_rate = models.FloatField(null=True, blank=True)
  trade_datetime = models.DateTimeField(null=True, blank=True)
  trade_rate = models.FloatField(null=True, blank=True)
  unit = models.CharField(max_length=10,default="JPY")
  profit = models.FloatField(null=True, blank=True)
  swap = models.FloatField(null=True, blank=True)
  memo = models.CharField(max_length=511)
  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=["account", "order_numver"],
        name="history_unique"
      )
    ]

  
