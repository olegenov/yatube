# Generated by Django 2.2.6 on 2020-09-07 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20200905_1736'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='autrhor',
            new_name='author',
        ),
    ]
