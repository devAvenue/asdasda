# Generated by Django 3.1.5 on 2021-05-17 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_notification_worker_workerwallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='trader',
            name='referral_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
