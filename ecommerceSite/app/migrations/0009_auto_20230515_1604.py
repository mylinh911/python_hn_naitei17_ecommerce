# Generated by Django 3.2.18 on 2023-05-15 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_remove_order_total_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderdetail',
            old_name='orderID',
            new_name='order',
        ),
        migrations.RenameField(
            model_name='orderdetail',
            old_name='productID',
            new_name='product',
        ),
    ]