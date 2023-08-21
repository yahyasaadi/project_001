from django.contrib import admin
from .models import OwnerDetails, PersonalDetails, FamilyBackaground, Sibling, AdditionalInformation, AcademicPerformance, Application, UploadedDocuments


class PersonalDetailsSearch(admin.ModelAdmin):
    # list_display = ('fullname', 'id_or_passport_no','institution','admin_no')
    search_fields = ['fullname', 'id_or_passport_no','institution','admin_no']


class FamilyBackagroundSearch(admin.ModelAdmin):
    # list_display = ('father_name','mother_full_name','guardian_full_name')
    search_fields = ['father_name','mother_full_name','guardian_full_name']

class SiblingSearch(admin.ModelAdmin):
    # list_display = ('sibling_name','institution')
    search_fields = ['sibling_name','institution']

class AdditionalInformationSearch(admin.ModelAdmin):
    # list_display = ('fund_secondary','prev_bursary','fund_college')
    search_fields = ['fund_secondary','prev_bursary','fund_college']

class AcademicPerformanceSearch(admin.ModelAdmin):
    # list_display = ('ref_one_name','ref_two_number')
    search_fields = ['ref_one_name','ref_two_number']

class UploadedDocumentsSearch(admin.ModelAdmin):
    # list_display = ('application','application_status')
    search_fields = ['application','application_status']


# Register your models here.
admin.site.register(OwnerDetails)
admin.site.register(Application)
admin.site.register(UploadedDocuments,UploadedDocumentsSearch)
admin.site.register(PersonalDetails,PersonalDetailsSearch)
admin.site.register(FamilyBackaground,FamilyBackagroundSearch)
admin.site.register(Sibling,SiblingSearch)
admin.site.register(AdditionalInformation,AdditionalInformationSearch)
admin.site.register(AcademicPerformance,AcademicPerformanceSearch)