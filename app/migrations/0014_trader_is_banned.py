# Generated by Django 3.1.5 on 2021-05-19 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_trader_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='trader',
            name='is_banned',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]