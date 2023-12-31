# Generated by Django 4.2.2 on 2023-09-04 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_personaldetails_education_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadeddocuments',
            name='approved_by',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='uploadeddocuments',
            name='urgency',
            field=models.CharField(choices=[('urgent', 'Urgent'), ('not_Urgent', 'Not Urgent')], default='not_Urgent', max_length=25),
        ),
    ]
