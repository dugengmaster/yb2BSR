# Generated by Django 5.0.6 on 2024-06-24 09:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0006_rename_first_name_userprofile_line_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="last_login_date",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="registration_date",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
