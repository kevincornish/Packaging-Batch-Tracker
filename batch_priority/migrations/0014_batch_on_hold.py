# Generated by Django 5.0.1 on 2024-01-17 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch_priority', '0013_batch_created_at_batch_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='on_hold',
            field=models.BooleanField(default=False),
        ),
    ]
