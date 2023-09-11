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
    p_o_box = models.CharField(max_length=255, null=True)
    p_o_box_location = models.CharField(max_length=255, null=True)
    location = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    generation_email = models.CharField(max_length=255, null=True)
    manager_email = models.CharField(max_length=255, null=True)
    name_of_the_chairperson = models.CharField(max_length=255, null=True)


    def __str__(self):
        return self.name
    
class PersonalDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    education_level = models.CharField(max_length=20,null=True ,choices=[('Secondary', 'Secondary'), ('Higher_Education', 'Higher Education')])
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
    sub_location = models.CharField(max_length=100,null=True)
    physical_address = models.CharField(max_length=100,null=True)
    permanent_address = models.CharField(max_length=100,null=True)
    ward = models.CharField(max_length=100)
    institution_postal_address = models.CharField(max_length=100)
    institution_telephone_no = models.CharField(max_length=100)
    ammount_requesting = models.CharField(max_length=100)

    def __str__(self):
        return self.user.first_name


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
        return self.user.first_name +' - ' + self.sibling_name
    

# models
class AdditionalInformation(models.Model):
    reason = models.TextField()
    prev_bursary = models.TextField(default='Not Received')
    org_bursary = models.TextField(default='Not Received')
    disability = models.TextField(default='No')
    chronic_illness = models.TextField(default='No')
    fam_disability = models.TextField(default='No')
    fam_chronic_illness = models.TextField(default='No')
    fund_secondary = models.TextField(null=True)
    fund_college = models.TextField(null=True)
    fund_uni = models.TextField(null=True)
    other_fund_secondary = models.TextField(null=True)
    other_fund_college = models.TextField(null=True)
    other_fund_uni = models.TextField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name


PERFORMANCE_LEVELS = [
    ('excellent', 'Excellent'),
    ('very_good', 'Very Good'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor')
]
class AcademicPerformance(models.Model):
    average_performance = models.CharField(max_length=50, choices=PERFORMANCE_LEVELS)
    sent_away = models.TextField()
    no_of_weeks = models.CharField(max_length=50)
    annual_fees = models.CharField(max_length=50)
    last_sem_fees = models.CharField(max_length=50)
    current_sem_fees = models.CharField(max_length=50)
    next_sem_fees = models.CharField(max_length=50)
    helb_loan = models.CharField(max_length=50, null=True)
    ref_one_name = models.CharField(max_length=100)
    ref_one_address = models.CharField(max_length=255)
    ref_one_number = models.CharField(max_length=40)
    ref_two_name = models.CharField(max_length=100)
    ref_two_address = models.CharField(max_length=255)
    ref_two_number = models.CharField(max_length=40)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.user.first_name
    

application_status = [
    ('Submitted', 'Submitted'),
    ('Under Review','Under Review'),
    ('Approved','Approved'),
    ('Rejected','Rejected'),
    ('Incomplete','Incomplete'),
    ('Funded','Funded'),
    ('Disbursed','Disbursed')
]




class Application(models.Model):
    id_for_reference = models.CharField(max_length=100, unique=True)
    name_of_application = models.CharField(max_length=200)
    number_of_applicant = models.IntegerField(null=True, default=0)
    funds_available_for_secondary_schools = models.IntegerField(null=True, default=0)
    funds_available_for_universities = models.IntegerField(null=True, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name_of_application + ' - which Started: ' + str(self.start_date) + ' and Ended: ' + str(self.end_date)

FUNDS_FOR = [
    ('Undefined','Undefined'),
    ('Secondary','Secondary'),
    ('Higher_Education','Higher Education')
]

class UploadedDocuments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    transcript_report_form = models.FileField(upload_to='documents/transcripts/',null=True)
    parents_guardians_id_card = models.FileField(upload_to='documents/id_cards/', blank=True, null=True)
    students_id_card = models.FileField(upload_to='documents/students_id_cards/', blank=True, null=True)
    id_card_birth_certificate = models.FileField(upload_to='documents/school_id_cards/', blank=True, null=True)
    parents_death_certificate = models.FileField(upload_to='documents/death_certificates/', blank=True, null=True)
    fees_structure = models.FileField(upload_to='documents/fees_structures/',null=True)
    admission_letters = models.FileField(upload_to='documents/admission_letters/', blank=True, null=True)
    verification_document = models.FileField(upload_to='documents/verification/', blank=True, null=True)
    application_status = models.CharField(max_length=50, default='Submitted', null=True,choices=application_status)
    funds_for = models.CharField(max_length=50, default='Undefined', null=True,choices=FUNDS_FOR)
    awarded = models.IntegerField(null=True, default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    approved_by = models.CharField(null= True,max_length=250)

    def __str__(self):
        return self.user.first_name  + ' ' + self.user.last_name + ' - '+self.application_status
    