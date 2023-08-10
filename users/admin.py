from django.contrib import admin
from .models import OwnerDetails, PersonalDetails, FamilyBackaground, Sibling

# Register your models here.
admin.site.register(OwnerDetails)
admin.site.register(PersonalDetails)
admin.site.register(FamilyBackaground)
admin.site.register(Sibling)