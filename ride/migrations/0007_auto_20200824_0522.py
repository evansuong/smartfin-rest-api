# Generated by Django 3.1 on 2020-08-24 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride', '0006_auto_20200822_0443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ridedata',
            name='motionData',
        ),
        migrations.RemoveField(
            model_name='ridedata',
            name='oceanData',
        ),
        migrations.AddField(
            model_name='ridedata',
            name='heightSmartfin',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ridedata',
            name='tempSmartfin',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
