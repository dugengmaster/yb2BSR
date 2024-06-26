# Generated by Django 5.0.6 on 2024-06-10 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapAPP', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tpe_yb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_no', models.CharField(max_length=20)),
                ('available_spaces', models.IntegerField()),
                ('isholiday', models.IntegerField()),
                ('rain_amt', models.FloatField()),
                ('temp_now', models.FloatField()),
                ('updated_at', models.CharField(max_length=20)),
                ('dc_time', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'tpe_yb',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Yb_cnty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=50)),
                ('area_code', models.CharField(max_length=10)),
                ('area_english', models.CharField(max_length=20)),
                ('bike_code', models.CharField(max_length=10)),
                ('station_start', models.IntegerField()),
                ('station_end', models.IntegerField()),
                ('domain', models.CharField(max_length=50)),
                ('is_open', models.IntegerField()),
                ('is_bind', models.IntegerField()),
                ('register_card', models.CharField(max_length=200)),
                ('contact_phone', models.CharField(max_length=200)),
                ('contact_mail', models.CharField(max_length=100)),
                ('ad_mail', models.CharField(max_length=100)),
                ('lat', models.CharField(max_length=20)),
                ('lng', models.CharField(max_length=20)),
                ('ride_count', models.IntegerField()),
                ('visit_count', models.IntegerField()),
                ('updated_at', models.CharField(max_length=20)),
                ('service_phone', models.CharField(max_length=20)),
                ('contact_phone_2', models.CharField(max_length=200)),
                ('ride_count2', models.IntegerField()),
                ('lat2', models.CharField(max_length=20)),
                ('lng2', models.CharField(max_length=20)),
                ('bike_type', models.CharField(max_length=20)),
                ('area_code_2', models.CharField(max_length=10)),
                ('area_name_tw', models.CharField(max_length=30)),
                ('area_name_en', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'yb_cnty',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Yb_stn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_code', models.CharField(max_length=10)),
                ('station_no', models.CharField(max_length=20)),
                ('name_tw', models.CharField(max_length=30)),
                ('district_tw', models.CharField(max_length=30)),
                ('address_tw', models.CharField(max_length=50)),
                ('name_en', models.CharField(max_length=30)),
                ('district_en', models.CharField(max_length=30)),
                ('address_en', models.CharField(max_length=50)),
                ('lat', models.CharField(max_length=20)),
                ('lng', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'yb_stn',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Yb_yb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField()),
                ('status', models.IntegerField()),
                ('station_no', models.CharField(max_length=20)),
                ('parking_spaces', models.IntegerField()),
                ('available_spaces', models.IntegerField()),
                ('available_spaces_detail', models.CharField(max_length=50)),
                ('available_spaces_level', models.IntegerField()),
                ('empty_spaces', models.IntegerField()),
                ('forbidden_spaces', models.IntegerField()),
                ('updated_at', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'yb_yb',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='ltecelltowertpe',
            options={},
        ),
    ]
