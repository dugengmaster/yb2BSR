# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class LtecelltowerTpe(models.Model):
    field_id = models.AutoField(db_column='_id', primary_key=True, blank=True, null=True)  # Field renamed because it started with '_'.
    radio = models.TextField()
    mcc = models.IntegerField()
    net = models.IntegerField()
    area = models.IntegerField()
    cell = models.IntegerField()
    unit = models.IntegerField()
    lon = models.TextField()  # This field type is a guess.
    lat = models.TextField()  # This field type is a guess.
    range = models.IntegerField()
    samples = models.IntegerField()
    changeable = models.IntegerField()
    created = models.IntegerField()
    updated = models.IntegerField()
    averagesignal = models.IntegerField(db_column='averageSignal')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'LTEcelltower_tpe'
