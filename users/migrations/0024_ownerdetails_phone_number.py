# Generated by Django 4.2.2 on 2023-09-07 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_ownerdetails_generation_email_ownerdetails_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownerdetails',
            name='phone_number',
            field=models.CharField(max_length=255, null=True),
        ),
    ]