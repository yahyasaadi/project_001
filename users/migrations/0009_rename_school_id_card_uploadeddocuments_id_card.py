# Generated by Django 4.2.2 on 2023-08-19 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_uploadeddocuments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploadeddocuments',
            old_name='school_id_card',
            new_name='id_card',
        ),
    ]