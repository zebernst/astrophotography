# Generated by Django 2.0.2 on 2018-03-26 17:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astrophotography', '0008_auto_20180326_0335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='del_hash',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='imgur deletion hash'),
        ),
        migrations.AlterField(
            model_name='image',
            name='imgur_url',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='link to imgur upload'),
        ),
        migrations.AlterField(
            model_name='image',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Location'),
        ),
        migrations.AlterField(
            model_name='image',
            name='waypoint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Waypoint'),
        ),
    ]
