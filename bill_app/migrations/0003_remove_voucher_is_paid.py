# Generated by Django 3.2 on 2023-04-14 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bill_app', '0002_voucher_cleared_bills'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voucher',
            name='is_paid',
        ),
    ]
