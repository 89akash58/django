
from django.db import models

class SalesData(models.Model):
    date = models.DateField()
    sales = models.IntegerField()

class CategoryData(models.Model):
    category = models.CharField(max_length=100)
    value = models.IntegerField()