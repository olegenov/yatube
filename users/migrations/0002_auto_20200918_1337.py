# Generated by Django 2.2.6 on 2020-09-18 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profilephoto',
            old_name='author',
            new_name='user',
        ),
    ]
