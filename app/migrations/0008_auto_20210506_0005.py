# Generated by Django 3.1.5 on 2021-05-06 00:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0007_auto_20210505_2256'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DBWallet',
            new_name='Wallet',
        ),
        migrations.AlterModelTable(
            name='wallet',
            table=None,
        ),
    ]
