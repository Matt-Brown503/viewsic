# Generated by Django 2.0.1 on 2018-02-27 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0016_auto_20180222_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='energy',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='energy_score',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
