# Generated by Django 3.1.5 on 2021-05-26 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20210526_0022'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
