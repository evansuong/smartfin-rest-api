# Generated by Django 3.1 on 2020-09-04 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride', '0011_auto_20200827_2001'),
    ]

    operations = [
        migrations.CreateModel(
            name='Buoys',
            fields=[
                ('buoyNum', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
