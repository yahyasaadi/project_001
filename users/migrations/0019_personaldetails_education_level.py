# Generated by Django 4.2.2 on 2023-09-02 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_application_number_of_applicant'),
    ]

    operations = [
        migrations.AddField(
            model_name='personaldetails',
            name='education_level',
            field=models.CharField(choices=[('Secondary', 'Secondary'), ('Higher_Education', 'Higher Education')], max_length=20, null=True),
        ),
    ]