# Generated by Django 4.1.7 on 2023-05-27 04:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fire_guard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='firealertservices',
            name='address',
            field=models.CharField(default=django.utils.timezone.now, max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firealertservices',
            name='is_rejected',
            field=models.BooleanField(default=False),
        ),
    ]