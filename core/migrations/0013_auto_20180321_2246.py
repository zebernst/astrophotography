# Generated by Django 2.0.2 on 2018-03-21 22:46

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('core', '0012_auto_20180321_2241'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commander',
            old_name='application_num',
            new_name='app_num',
        ),
    ]
