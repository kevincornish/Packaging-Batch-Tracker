# Generated by Django 5.0.1 on 2024-01-13 16:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch_priority', '0003_alter_targetdate_bay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='product_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batch_priority.product'),
        ),
    ]
