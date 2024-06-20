# Generated by Django 5.0.6 on 2024-06-10 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Line_Official_Account_Bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineUserSessions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=50)),
                ('expiry_date', models.BigIntegerField()),
                ('task', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('expired', 'expired'), ('completed', 'completed')], default='pending', max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='weatherrecord',
            name='location',
            field=models.CharField(max_length=50),
        ),
    ]