# Generated by Django 4.1.1 on 2022-10-26 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_productimage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(default='', help_text='Required', max_length=255, verbose_name='brand'),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=0, default=0, error_messages={'name': {'max_length': 'The rating must be between 0 and 5.'}}, help_text='Maximum 5', max_digits=2, verbose_name='rating'),
        ),
        migrations.AddField(
            model_name='product',
            name='rating_number',
            field=models.IntegerField(default=0, verbose_name='Total number of ratings'),
        ),
    ]