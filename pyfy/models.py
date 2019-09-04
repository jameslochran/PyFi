from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Portfolio(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    retirement = 'Retirement'
    vacation =  'Vacation'
    savings  = 'Savings'
    education = 'Education'
    house = 'House'
    investment = 'Investment'
    PORTTYPE = (
                (retirement, 'Retirement'),
                (vacation,  'Vacation'),
                (savings, 'Savings'),
                (education, 'Education'),
                (house, 'House'),
                (investment, 'Investment')
                )
    type = models.CharField(("Portfolio Type"), max_length=100, choices=PORTTYPE, default='Retirement')

    def __str__(self):
    	return self.title


class Stock(models.Model):
    ticker = models.CharField(max_length=255)
    count = models.IntegerField(default=1)
    acq_date = models.DateField(default=date.today)
    unit_cost = models.FloatField(default=1.00)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)


    def __str__(self):
        return (self.ticker)

    def price(self):
        import json
        import requests

        price = 0
        quant = self.count
        ticker = self.ticker
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/"+ ticker +"/quote?token=pk_5a6bfc8f3d3d405f910aec024cc2bc14")

        try:
            api = json.loads(api_request.content)
            price = api["latestPrice"]


        except Exception as e:
            api = "Error...."


        return price

    def total(self):
        q = self.count
        p =  self.price


        # total = q*p
        return p
