# Generated by Django 3.2 on 2023-04-15 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bill_app', '0004_auto_20230415_0948'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bill',
            unique_together={('bill_meter', 'bill_date')},
        ),
    ]
