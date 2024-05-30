# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class LtecelltowerTpe(models.Model):
    _id = models.AutoField(db_column='_id', primary_key=True)
    radio = models.TextField()
    mcc = models.IntegerField()
    net = models.IntegerField()
    area = models.IntegerField()
    cell = models.IntegerField()
    unit = models.IntegerField()
    lon = models.FloatField() 
    lat = models.FloatField()  
    range = models.IntegerField()
    samples = models.IntegerField()
    changeable = models.IntegerField()
    created = models.IntegerField()
    updated = models.IntegerField()
    averagesignal = models.IntegerField(db_column='averageSignal')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'LTEcelltower_tpe'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class TpeYb(models.Model):
    station_no = models.CharField(max_length=20)
    available_spaces = models.IntegerField()
    isholiday = models.IntegerField()
    rain_amt = models.FloatField()
    updated_at = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'tpe_yb'


class YbCnty(models.Model):
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
        managed = False
        db_table = 'yb_cnty'


class YbStn(models.Model):
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
        managed = False
        db_table = 'yb_stn'
