# Generated by Django 5.1.1 on 2024-11-03 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_withdrawrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='rvid',
            field=models.TextField(null=True),
        ),
    ]
