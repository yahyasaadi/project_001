from django.db import models
from django.contrib.auth.models import User


family_status_choices = [
        ('both_parents_dead', 'Both Parents Dead'),
        ('one_parent_dead', 'One Parent Dead'),
        ('both_parents_alive', 'Both Parents Alive'),
        ('single_parent', 'Single Parent'),
        ('others', 'Others'),
    ]    
father_employment_choices = [
    ('permanent', 'Permanent'),
    ('contractual', 'Contractual'),
    ('casual', 'Casual'),
    ('retired', 'Retired'),
    ('self_employed', 'Self Employed'),
    ('none', 'None'),
]
mother_employment_choices = [
        ('permanent', 'Permanent'),
        ('contractual', 'Contractual'),
        ('casual', 'Casual'),
        ('retired', 'Retired'),
        ('self_employed', 'Self Employed'),
        ('none', 'None'),
    ]

guardian_employment_choices = [
        ('permanent', 'Permanent'),
        ('contractual', 'Contractual'),
        ('casual', 'Casual'),
        ('retired', 'Retired'),
        ('self_employed', 'Self Employed'),
        ('none', 'None'),
    ]




# Create your models here.
class OwnerDetails(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    county = models.CharField(max_length=100)


    def __str__(self):
        return self.name
    
class PersonalDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    id_or_passport_no = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    date_of_birth = models.DateField()
    institution = models.CharField(max_length=255)
    admin_no = models.CharField(max_length=255)
    campus_or_branch = models.CharField(max_length=255)
    faculty = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    course_duration = models.CharField(max_length=255)
    mode_of_study = models.CharField(max_length=20, choices=[('regular', 'Regular'), ('part_time', 'Part Time'),('parallel','Parallel'),('boarding','Boarding'),('day','Day'),('online','Online')])
    year_of_study = models.CharField(max_length=20)
    year_of_completion = models.CharField(max_length=50)
    mobile_no = models.CharField(max_length=20)
    name_polling_station = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    institution_postal_address = models.CharField(max_length=100)
    institution_telephone_no = models.CharField(max_length=100)
    ammount_requesting = models.CharField(max_length=100)

    def __str__(self):
        return self.fullname


class FamilyBackaground(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    family_status = models.CharField(max_length=30, choices=family_status_choices)
    number_siblings = models.CharField(max_length=10)
    family_income = models.CharField(max_length=10)
    family_expense = models.CharField(max_length=10)
    father_name = models.CharField(max_length=250)
    father_address = models.CharField(max_length=250)
    father_mobile_no = models.CharField(max_length=250)
    father_occupation = models.CharField(max_length=250)
    father_type_of_employment = models.CharField(max_length=30, choices=father_employment_choices)
    father_main_source_of_income = models.CharField(max_length=100)
    mother_full_name = models.CharField(max_length=100)
    mother_address = models.CharField(max_length=200)
    mother_telephone_number = models.CharField(max_length=15)
    mother_occupation = models.CharField(max_length=100)
    mother_type_of_employment = models.CharField(max_length=30, choices=mother_employment_choices)
    mother_main_source_of_income = models.CharField(max_length=100)

    #guardian info
    guardian_full_name = models.CharField(max_length=100)
    guardian_address = models.CharField(max_length=200)
    guardian_telephone_number = models.CharField(max_length=15)
    guardian_occupation = models.CharField(max_length=100)

    guardian_type_of_employment = models.CharField(max_length=30, choices=guardian_employment_choices)
    guardian_main_source_of_income = models.CharField(max_length=100)


    def __str__(self):
        return self.user.first_name



class Sibling(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='siblings')
    sibling_name = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    fees = models.CharField(max_length=200)

    def __str__(self):
        return self.user.first_name +' '+ self.user.last_name
