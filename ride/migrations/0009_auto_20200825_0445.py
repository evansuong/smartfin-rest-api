# Generated by Django 3.1 on 2020-08-25 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride', '0008_auto_20200825_0426'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ridedata',
            old_name='heightListSmartfin',
            new_name='heightList',
        ),
        migrations.RenameField(
            model_name='ridedata',
            old_name='tempListSmartfin',
            new_name='tempList',
        ),
        migrations.AddField(
            model_name='ridedata',
            name='heightSampleRate',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ridedata',
            name='tempSampleRate',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
