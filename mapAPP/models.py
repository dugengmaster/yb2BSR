# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class LtecelltowerTpe(models.Model):
    field_id = models.AutoField(
        db_column="_id", primary_key=True
    )  # Field renamed because it started with '_'.
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
    averagesignal = models.IntegerField(
        db_column="averageSignal"
    )  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = "LTEcelltower_tpe"


class Yb_cnty(models.Model):
    uid = models.CharField(max_length=50)
    area_code = models.CharField(max_length=10)
    area_english = models.CharField(max_length=20)
    bike_code = models.CharField(max_length=10)
    station_start = models.IntegerField()
    station_end = models.IntegerField()
    domain = models.CharField(max_length=50)
    is_open = models.IntegerField()
    is_bind = models.IntegerField()
    register_card = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=200)
    contact_mail = models.CharField(max_length=100)
    ad_mail = models.CharField(max_length=100)
    lat = models.CharField(max_length=20)
    lng = models.CharField(max_length=20)
    ride_count = models.IntegerField()
    visit_count = models.IntegerField()
    updated_at = models.CharField(max_length=20)
    service_phone = models.CharField(max_length=20)
    contact_phone_2 = models.CharField(max_length=200)
    ride_count2 = models.IntegerField()
    lat2 = models.CharField(max_length=20)
    lng2 = models.CharField(max_length=20)
    bike_type = models.CharField(max_length=20)
    area_code_2 = models.CharField(max_length=10)
    area_name_tw = models.CharField(max_length=30)
    area_name_en = models.CharField(max_length=30)

    class Meta:
        db_table = "yb_cnty"
        managed = False


class Yb_stn(models.Model):
    area_code = models.CharField(max_length=10)
    station_no = models.CharField(max_length=20)
    name_tw = models.CharField(max_length=30)
    district_tw = models.CharField(max_length=30)
    address_tw = models.CharField(max_length=50)
    name_en = models.CharField(max_length=30)
    district_en = models.CharField(max_length=30)
    address_en = models.CharField(max_length=50)
    lat = models.CharField(max_length=20)
    lng = models.CharField(max_length=20)

    class Meta:
        db_table = "yb_stn"
        managed = False


class Yb_yb(models.Model):
    type = models.IntegerField()
    status = models.IntegerField()
    station_no = models.CharField(max_length=20)
    parking_spaces = models.IntegerField()
    available_spaces = models.IntegerField()
    available_spaces_detail = models.CharField(max_length=50)
    available_spaces_level = models.IntegerField()
    empty_spaces = models.IntegerField()
    forbidden_spaces = models.IntegerField()
    updated_at = models.CharField(max_length=20)

    class Meta:
        db_table = "yb_yb"
        managed = False


# set up the yb model by using Teipei's data
class Tpe_yb(models.Model):
    station_no = models.CharField(max_length=20)
    available_spaces = models.IntegerField()
    isholiday = models.IntegerField()
    rain_amt = models.FloatField()
    temp_now = models.FloatField()
    updated_at = models.CharField(max_length=20)
    dc_time = models.CharField(max_length=20)

    class Meta:
        db_table = "tpe_yb"
        managed = False
