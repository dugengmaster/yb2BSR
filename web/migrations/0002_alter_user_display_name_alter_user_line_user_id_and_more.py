# Generated by Django 5.0.6 on 2024-06-08 05:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="display_name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="user",
            name="line_user_id",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="picture_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]