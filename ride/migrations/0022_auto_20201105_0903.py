# Generated by Django 3.1 on 2020-11-05 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride', '0021_auto_20201105_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ridedata',
            name='buoyCDIP',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
