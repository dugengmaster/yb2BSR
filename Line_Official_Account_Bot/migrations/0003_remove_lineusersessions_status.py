# Generated by Django 5.0.6 on 2024-06-10 22:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Line_Official_Account_Bot', '0002_lineusersessions_alter_weatherrecord_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lineusersessions',
            name='status',
        ),
    ]
