# Generated by Django 3.1.5 on 2021-05-19 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_trader_is_banned'),
    ]

    operations = [
        migrations.AddField(
            model_name='trader',
            name='terms_text',
            field=models.TextField(null=True),
        ),
    ]
