# Generated by Django 5.0.6 on 2024-06-25 02:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0009_remove_userprofile_last_login_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="username",
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]
