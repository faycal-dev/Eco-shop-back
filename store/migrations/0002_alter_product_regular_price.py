# Generated by Django 4.1.1 on 2022-11-07 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='regular_price',
            field=models.DecimalField(decimal_places=2, error_messages={'name': {'max_length': 'The price must be between 0 and 99999.99.'}}, help_text='Maximum 99999.99', max_digits=10, verbose_name='Regular price'),
        ),
    ]
