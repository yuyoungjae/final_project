# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'category'

class Menu(models.Model):
    name = models.CharField(max_length=20)
    price = models.IntegerField()
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    image = models.TextField()

    class Meta:
        managed = False
        db_table = 'menu'


class Orderdetail(models.Model):
    orderinfo = models.ForeignKey('Orderinfo', models.DO_NOTHING, blank=True, null=True)
    menu = models.ForeignKey(Menu, models.DO_NOTHING, blank=True, null=True)
    amount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'orderdetail'


class Orderinfo(models.Model):
    weather = models.CharField(max_length=20)
    process_time = models.TimeField()
    order_time = models.DateTimeField()
    senior = models.CharField(max_length=10)
    gender = models.CharField(max_length=2)
    shelter = models.ForeignKey('Shelter', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'orderinfo'


class Shelter(models.Model):
    name = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        managed = False
        db_table = 'shelter'
