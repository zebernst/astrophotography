# Generated by Django 2.0.2 on 2018-02-22 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astrophotography', '0004_auto_20180209_0344'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='del_hash',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='edited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='image',
            name='imgur_url',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
