# Generated by Django 2.2.6 on 2020-09-18 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200918_1337'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProfilePhoto',
        ),
    ]