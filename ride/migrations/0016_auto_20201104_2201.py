# Generated by Django 3.1 on 2020-11-04 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ride', '0015_auto_20201104_1948'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Buoys',
            new_name='Buoy',
        ),
        migrations.AlterField(
            model_name='ridedata',
            name='motionData',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='ridedata',
            name='oceanData',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='ZippedDataframe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filePath', models.CharField(blank=True, max_length=50, null=True)),
                ('dataType', models.CharField(blank=True, max_length=10, null=True)),
                ('rideId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ride.ridedata')),
            ],
        ),
    ]
