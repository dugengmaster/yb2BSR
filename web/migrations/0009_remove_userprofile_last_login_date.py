# Generated by Django 5.0.6 on 2024-06-24 10:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0008_remove_userprofile_user_userprofile_last_login"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="last_login_date",
        ),
    ]
