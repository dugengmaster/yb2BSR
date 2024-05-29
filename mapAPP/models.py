from django.db import models

# Create your models here.


#yb data collection for prediction model setup
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

#set up the yb model by using Teipei's data
class Tpe_yb(models.Model):
    station_no = models.CharField(max_length=20)
    available_spaces = models.IntegerField()
    isholiday= models.IntegerField()
    rain_amt=models.FloatField()
    temp_now=models.FloatField()
    updated_at = models.CharField(max_length=20)
    dc_time = models.CharField(max_length=20)

    class Meta:
        db_table = "tpe_yb"