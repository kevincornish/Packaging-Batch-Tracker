# Generated by Django 5.0.2 on 2024-02-22 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch_priority', '0025_tray_tray_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='expected_yield',
            field=models.IntegerField(null=True),
        ),
    ]