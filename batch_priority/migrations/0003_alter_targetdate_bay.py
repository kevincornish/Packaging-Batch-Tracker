# Generated by Django 5.0.1 on 2024-01-13 16:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch_priority', '0002_bay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetdate',
            name='bay',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batch_priority.bay'),
        ),
    ]
