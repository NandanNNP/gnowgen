# Generated by Django 5.1.1 on 2024-10-28 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_customuser_is_verified_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]