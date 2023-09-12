from django.shortcuts import render, redirect, HttpResponse
from django.shortcuts import  get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.template.defaultfilters import date
# from django.conf import settings
from CDF import settings
from itertools import groupby

# from django.http import HttpResponse
from .tokens import generate_token
from .models import (
    OwnerDetails,
    PersonalDetails,
    FamilyBackaground,
    Sibling,
    AdditionalInformation,
    AcademicPerformance,
    Application,
    UploadedDocuments
    )
from fpdf import FPDF
from datetime import datetime
from num2words import num2words

# Create your views here.
@login_required
def home(request):
    owner = OwnerDetails.objects.first()
    last_application = Application.objects.last()
    try:
        already = UploadedDocuments.objects.get(user=request.user,application=last_application)   
    except UploadedDocuments.DoesNotExist:
        already = None
    
    if already is not None:
        return redirect('apply')
    else:
        return render(request, "users/home.html",{'owner':owner})

def signup(request):
    owner = OwnerDetails.objects.last()
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists. Try again!")
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered. Use another email.")
            return redirect('signup')
        
        if len(username) > 10 or len(username) < 3:
            messages.error(request, "Username must be between 3 to 10 characters long!")
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request, "Passwords did not match!")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha Numeric!")
            return redirect('signup')

        new_user = User.objects.create_user(username, email, pass1)
        new_user.first_name = fname
        new_user.last_name = lname
        new_user.is_active = False
        new_user.save()
        messages.success(request, "Account Created Successfully. Activation Link has been Sent to your Email. Please Confirm.")


       
        # welcome email
        email = EmailMessage(
            subject=f"Welcome to {owner.county} Portal!!",
            body="Hello " + new_user.first_name + "!! \n" + f"Welcome to {owner.county}. \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address. \n\nThanking You\n{owner.name_of_the_chairperson}, Chairperson.",
            from_email=settings.EMAIL_HOST_USER,
            to=[new_user.email],
        )
        # email.fail_silently = True
        email.send()


        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = f"Confirm your Email @ {owner.county}!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': new_user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
            'token': generate_token.make_token(new_user)
        })
        email = EmailMessage(
        subject=email_subject,
        body=message2,
        from_email=settings.EMAIL_HOST_USER,
        to=[new_user.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('signin')
    
    if not request.user.is_authenticated:
        context = {
            'owner':owner
        }
        return render(request, "users/signup.html",context)
    return redirect('signin')



def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('students_dashboard')
    else:
        context = {
            'owner':OwnerDetails.objects.last()
        }
        return render(request,'activation_failed.html',context)
    

@login_required
def studentsDashboard(request):
    fname = request.user.first_name
    owner = OwnerDetails.objects.first()
    last_application = Application.objects.last()
    try:
        already = UploadedDocuments.objects.get(user=request.user,application=last_application)   
    except UploadedDocuments.DoesNotExist:
        already = None
    
    if already is not None:
        return redirect('apply')
    else:
        # return redirect('students_dashboard')
        return render(request, 'users/students_dashboard.html',{'fname':fname,'owner':owner})

@login_required
def family_background(request):
    if request.method == 'POST':
        family_status = request.POST['family_status']
        number_siblings = request.POST['number_siblings']
        family_income = request.POST['family_income']
        family_expense = request.POST['family_expense']
        father_name = request.POST['father_name']
        father_address = request.POST['father_address']
        father_mobile_no = request.POST['father_mobile_no']
        father_occupation = request.POST['father_occupation']
        father_type_of_employment = request.POST['father_type_of_employment']
        father_main_source_of_income = request.POST['father_main_source_of_income']
        mother_full_name = request.POST['mother_full_name']
        mother_address = request.POST['mother_address']
        mother_telephone_number = request.POST['mother_telephone_number']
        mother_occupation = request.POST['mother_occupation']
        mother_type_of_employment = request.POST['mother_type_of_employment']
        mother_main_source_of_income = request.POST['mother_main_source_of_income']
        guardian_full_name = request.POST['guardian_full_name']
        guardian_address = request.POST['guardian_address']
        guardian_telephone_number = request.POST['guardian_telephone_number']
        guardian_occupation = request.POST['guardian_occupation']
        guardian_type_of_employment = request.POST['guardian_type_of_employment']
        guardian_main_source_of_income = request.POST['guardian_main_source_of_income']
        user = request.user

        saving_family_bg = FamilyBackaground(
            user=user,
            family_status=family_status,
            number_siblings=number_siblings,
            family_income=family_income,
            family_expense=family_expense,
            father_name=father_name,
            father_address=father_address,
            father_mobile_no=father_mobile_no,
            father_occupation=father_occupation,
            father_type_of_employment=father_type_of_employment,
            father_main_source_of_income=father_main_source_of_income,
            mother_full_name=mother_full_name,
            mother_address=mother_address,
            mother_telephone_number=mother_telephone_number,
            mother_occupation=mother_occupation,
            mother_type_of_employment=mother_type_of_employment,
            mother_main_source_of_income=mother_main_source_of_income,
            guardian_full_name=guardian_full_name,
            guardian_address=guardian_address,
            guardian_telephone_number=guardian_telephone_number,
            guardian_occupation=guardian_occupation,
            guardian_type_of_employment=guardian_type_of_employment,
            guardian_main_source_of_income=guardian_main_source_of_income
        )
        saved = saving_family_bg.save()


        sibling_names = request.POST.getlist('name[]')
        sibling_institutions = request.POST.getlist('institution[]')
        sibling_fees = request.POST.getlist('fees[]')

        for i in range(len(sibling_names)):
            sibling_name = sibling_names[i]
            sibling_institution = sibling_institutions[i]
            sibling_fee = sibling_fees[i]

            saving_sibling = Sibling(
                user=request.user,
                sibling_name=sibling_name,
                institution= sibling_institution,
                fees=sibling_fee
,
            )
            saving_sibling.save()
        return redirect('additional_info')
    else:
        owner = OwnerDetails.objects.first()
        family_background = FamilyBackaground.objects.filter(user = request.user).exists()
        if family_background is True:
            return redirect('update_family_background')
        return render(request, 'users/family_background.html',{"owner":owner})


@login_required
def update_family_background(request):
    if request.method == 'POST':
        family_status = request.POST['family_status']
        number_siblings = request.POST['number_siblings']
        family_income = request.POST['family_income']
        family_expense = request.POST['family_expense']
        father_name = request.POST['father_name']
        father_address = request.POST['father_address']
        father_mobile_no = request.POST['father_mobile_no']
        father_occupation = request.POST['father_occupation']
        father_type_of_employment = request.POST['father_type_of_employment']
        father_main_source_of_income = request.POST['father_main_source_of_income']
        mother_full_name = request.POST['mother_full_name']
        mother_address = request.POST['mother_address']
        mother_telephone_number = request.POST['mother_telephone_number']
        mother_occupation = request.POST['mother_occupation']
        mother_type_of_employment = request.POST['mother_type_of_employment']
        mother_main_source_of_income = request.POST['mother_main_source_of_income']
        guardian_full_name = request.POST['guardian_full_name']
        guardian_address = request.POST['guardian_address']
        guardian_telephone_number = request.POST['guardian_telephone_number']
        guardian_occupation = request.POST['guardian_occupation']
        guardian_type_of_employment = request.POST['guardian_type_of_employment']
        guardian_main_source_of_income = request.POST['guardian_main_source_of_income']
        user = request.user

        updating = FamilyBackaground.objects.filter(user=user).update(
            user=user,
            family_status=family_status,
            number_siblings=number_siblings,
            family_income=family_income,
            family_expense=family_expense,
            father_name=father_name,
            father_address=father_address,
            father_mobile_no=father_mobile_no,
            father_occupation=father_occupation,
            father_type_of_employment=father_type_of_employment,
            father_main_source_of_income=father_main_source_of_income,
            mother_full_name=mother_full_name,
            mother_address=mother_address,
            mother_telephone_number=mother_telephone_number,
            mother_occupation=mother_occupation,
            mother_type_of_employment=mother_type_of_employment,
            mother_main_source_of_income=mother_main_source_of_income,
            guardian_full_name=guardian_full_name,
            guardian_address=guardian_address,
            guardian_telephone_number=guardian_telephone_number,
            guardian_occupation=guardian_occupation,
            guardian_type_of_employment=guardian_type_of_employment,
            guardian_main_source_of_income=guardian_main_source_of_income
        )
        x= Sibling.objects.filter()
        x.delete()
        sibling_names = request.POST.getlist('name[]')
        sibling_institutions = request.POST.getlist('institution[]')
        sibling_fees = request.POST.getlist('fees[]')

        for i in range(len(sibling_names)):
            sibling_name = sibling_names[i]
            sibling_institution = sibling_institutions[i]
            sibling_fee = sibling_fees[i]

            saving_sibling = Sibling(
                user=request.user,
                sibling_name=sibling_name,
                institution= sibling_institution,
                fees=sibling_fee
,
            )
            saving_sibling.save()
        print(updating)
        if updating:
            # print(updating)
            return redirect('additional_info')
        else:
            print('not updated')
            return render(request, 'users/family_backgroundUpdate.html',{"owner":owner,'family_background':family_background})

    else:
        owner = OwnerDetails.objects.first() 
        family_background = FamilyBackaground.objects.get(user=request.user)
        siblings = Sibling.objects.filter(user=request.user)
        # print(request.user)
        return render(request, 'users/family_backgroundUpdate.html',{"owner":owner,'family_background':family_background,'siblings':siblings})



@login_required
def personal_details(request):
    if request.method == 'POST':
        user = request.user
        fullname = request.POST['fullname']
        education_level = request.POST['education_level']
        id_or_passport_no = request.POST['id_or_passport_no']
        gender = request.POST['gender']
        date_of_birth = request.POST['date_of_birth']
        institution = request.POST['institution']

        admin_no = request.POST['admin_no']
        campus_or_branch = request.POST['campus_or_branch']
        faculty = request.POST['faculty']
        course = request.POST['course']
        course_duration = request.POST['course_duration']

        mode_of_study = request.POST['mode_of_study']
        year_of_study = request.POST['year_of_study']
        year_of_completion = request.POST['year_of_completion']
        mobile_no = request.POST['mobile_no']
        name_polling_station = request.POST['name_polling_station']

        location = request.POST['location']
        sub_location = request.POST['sub_location']
        ward = request.POST['ward']
        physical_address = request.POST['physical_address']
        permanent_address = request.POST['permanent_address']
        institution_postal_address = request.POST['institution_postal_address']
        institution_telephone_no = request.POST['institution_telephone_no']
        ammount_requesting = request.POST['ammount_requesting']

        saving_personal_details = PersonalDetails(
            user=user,
            fullname=fullname,
            education_level=education_level,
            id_or_passport_no= id_or_passport_no,
            gender=gender,
            date_of_birth=date_of_birth,
            institution=institution.upper(),
            admin_no=admin_no,
            campus_or_branch=campus_or_branch,
            faculty=faculty,
            course=course,
            course_duration=course_duration,
            mode_of_study=mode_of_study,
            year_of_study=year_of_study,
            year_of_completion=year_of_completion,
            mobile_no=mobile_no,
            name_polling_station=name_polling_station,
            location=location,
            sub_location=sub_location,
            ward=ward,
            physical_address=physical_address,
            permanent_address=permanent_address,
            institution_postal_address= institution_postal_address,
            institution_telephone_no=institution_telephone_no,
            ammount_requesting=ammount_requesting
        )
        saved = saving_personal_details.save()

        return redirect('family_background')

    else:
        owner = OwnerDetails.objects.first()
        personal_details = PersonalDetails.objects.filter(user = request.user).exists()
        if personal_details is True:
            return redirect('update_personal_details')
        return render(request, 'users/personal_details.html',{"owner":owner})

@login_required
def update_personal_details(request):
    if request.method == 'POST':
        user = request.user
        print(user)
        fullname = request.POST['fullname']
        education_level = request.POST['education_level']
        
        id_or_passport_no = request.POST['id_or_passport_no']
        gender = request.POST['gender']
        date_of_birth = request.POST['date_of_birth']
        institution = request.POST['institution']

        admin_no = request.POST['admin_no']
        campus_or_branch = request.POST['campus_or_branch']
        faculty = request.POST['faculty']
        course = request.POST['course']
        course_duration = request.POST['course_duration']

        mode_of_study = request.POST['mode_of_study']
        year_of_study = request.POST['year_of_study']
        year_of_completion = request.POST['year_of_completion']
        mobile_no = request.POST['mobile_no']
        name_polling_station = request.POST['name_polling_station']

        location = request.POST['location']
        sub_location = request.POST['sub_location']
        ward = request.POST['ward']
        physical_address = request.POST['physical_address']
        permanent_address = request.POST['permanent_address']
        institution_postal_address = request.POST['institution_postal_address']
        institution_telephone_no = request.POST['institution_telephone_no']
        ammount_requesting = request.POST['ammount_requesting']

        updating = PersonalDetails.objects.filter(user=user).update(
            user=user,
            fullname=fullname,
            education_level=education_level,
            id_or_passport_no= id_or_passport_no,
            gender=gender,
            date_of_birth=date_of_birth,
            institution=institution.upper(),
            admin_no=admin_no,
            campus_or_branch=campus_or_branch,
            faculty=faculty,
            course=course,
            course_duration=course_duration,
            mode_of_study=mode_of_study,
            year_of_study=year_of_study,
            year_of_completion=year_of_completion,
            mobile_no=mobile_no,
            name_polling_station=name_polling_station,
            location=location,
            sub_location=sub_location,
            ward=ward,
            physical_address=physical_address,
            permanent_address=permanent_address,
            institution_postal_address= institution_postal_address,
            institution_telephone_no=institution_telephone_no,
            ammount_requesting=ammount_requesting
        )
        
        print(updating)
        if updating:
            print(updating)
            return redirect('family_background')

        else:
            print('not updated')
            return render(request, 'users/personal_detailsUpdate.html',{"owner":owner,'personal_details':personal_details})


    else:
        owner = OwnerDetails.objects.first() 
        personal_details = PersonalDetails.objects.get(user=request.user)
        # print(request.user)
        return render(request, 'users/personal_detailsUpdate.html',{"owner":owner,'personal_details':personal_details})



def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)

            if user.is_staff:
                messages.success(request, f"{username} - Logged In Successfully!!")
                return redirect('staff_dashboard')
            
            messages.success(request, f"{username} - Logged In Successfully!!")
            return redirect('students_dashboard')
        else:

            if User.objects.filter(username=username,is_active = False):
                messages.error(request, "Please Activate your account first.")
                return redirect('signin')

            else:   
                messages.error(request, "Invalid username or password.")
                return redirect('signin')
    else:
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('staff_dashboard')
            else:
                return redirect('students_dashboard')
        else:
            owner = OwnerDetails.objects.first()  
            return render(request, "users/signin.html",{'owner':owner})



@login_required
def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('signin')


# the views
@login_required
def additional_info(request):
    if request.method == "POST":
        reason = request.POST['reason']
        prev_bursary = request.POST['prev_bursary']
        org_bursary = request.POST['org_bursary']
        disability = request.POST['disability']
        chronic_illness = request.POST['chronic_illness']
        fam_disability = request.POST['fam_disability']
        fam_chronic_illness = request.POST['fam_chronic_illness']
        fund_secondary = request.POST['fund_secondary']
        fund_college = request.POST['fund_college']
        fund_uni = request.POST['fund_uni']
        other_fund_secondary = request.POST['other_fund_secondary']
        other_fund_college = request.POST['other_fund_college']
        other_fund_uni = request.POST['other_fund_uni']

        if prev_bursary == '':
            prev_bursary = "Not Received"

        if org_bursary == '':
            org_bursary = "Not Received"

        if disability == '':
            disability = "No"

        if chronic_illness == '':
            chronic_illness = "No"

        if fam_disability == '':
            fam_disability = "No"

        if fam_chronic_illness == '':
            fam_chronic_illness = "No"

        

        additional_info = AdditionalInformation(
            user=request.user,
            reason=reason,
            prev_bursary = prev_bursary,
            org_bursary = org_bursary,
            disability = disability,
            chronic_illness = chronic_illness,
            fam_disability = fam_disability,
            fam_chronic_illness = fam_chronic_illness,
            fund_secondary = fund_secondary,
            fund_college = fund_college,
            fund_uni = fund_uni,
            other_fund_secondary = other_fund_secondary,
            other_fund_college = other_fund_college,
            other_fund_uni = other_fund_uni
        )
        additional_info.save()
        return redirect("academic_performance")
    else:
        owner = OwnerDetails.objects.first() 
        additional_info = AdditionalInformation.objects.filter(user=request.user).exists()
        if additional_info is True:
            return redirect('update_additional_info')
        else:
            return render(request, 'users/additional_info.html',{"owner":owner})



@staff_member_required
def staff_dashboard(request):
    user = request.user
    fname = user.first_name
    owner = OwnerDetails.objects.last()
    peronal_details = PersonalDetails.objects.all()
    family_background = FamilyBackaground.objects.all()
    additional_info = AdditionalInformation.objects.all()
    academic_performance = AcademicPerformance.objects.all()
    application = Application.objects.last()
    uploaded_documents = UploadedDocuments.objects.all()

    funds_available_for_universities = application.funds_available_for_universities
    funds_available_for_secondary_schools = application.funds_available_for_secondary_schools

    funds_available_for_secondary_schools = "{:,}".format(funds_available_for_secondary_schools)
    funds_available_for_universities = "{:,}".format(funds_available_for_universities)


    approved_applicants_count = UploadedDocuments.objects.filter(application_status='Approved',application=application).count()

    # approved_sum = UploadedDocuments.objects.filter(application_status='Approved',application=application).aggregate(Sum('awarded'))['awarded__sum']
    application_statuses = ['Approved', 'Funded', 'Disbursed']
    approved_sum = UploadedDocuments.objects.filter(application_status__in=application_statuses, application=application).aggregate(Sum('awarded'))['awarded__sum']
    approved_sum_secondary = UploadedDocuments.objects.filter(application_status__in=application_statuses,funds_for='Secondary',application=application).aggregate(Sum('awarded'))['awarded__sum']

    approved_sum_higher_education = UploadedDocuments.objects.filter(application_status__in=application_statuses, funds_for='Higher_Education',application=application).aggregate(Sum('awarded'))['awarded__sum']
    
    approved_user_ids = UploadedDocuments.objects.filter(application_status='Approved', application=application).values_list('user_id', flat=True)

    disbursed_ed_user_ids = UploadedDocuments.objects.filter(application_status='Disbursed', application=application).values_list('user_id', flat=True)
    disbursed_users_personal_details = PersonalDetails.objects.filter(user_id__in=disbursed_ed_user_ids)
    status_for_all_disbursed = UploadedDocuments.objects.filter(user_id__in=disbursed_ed_user_ids)



    approved_users_personal_details = PersonalDetails.objects.filter(user_id__in=approved_user_ids)
    funds_for_all_user = UploadedDocuments.objects.filter(user_id__in=approved_user_ids)


    applied_user_ids = UploadedDocuments.objects.filter( application=application).values_list('user_id', flat=True)
    applied_users_personal_details = PersonalDetails.objects.filter(user_id__in=applied_user_ids)
    status_for_all_user = UploadedDocuments.objects.filter(user_id__in=applied_user_ids)


    return render(
        request,
        'users/staff_page.html',
        {
            "fname":fname,
            'owner':owner,
            'peronal_details':peronal_details,
            'family_background':family_background,
            'additional_info':additional_info,
            'academic_performance':academic_performance,
            'academic_performance':academic_performance,
            'application':application,
            'uploaded_documents':uploaded_documents,
            'funds_available_for_secondary_schools':funds_available_for_secondary_schools,
            'funds_available_for_universities':funds_available_for_universities,
            'approved_applicants_count':approved_applicants_count,
            'approved_sum':approved_sum,
            'approved_sum_secondary':approved_sum_secondary,
            'approved_sum_higher_education':approved_sum_higher_education,
            'approved_users_personal_details':approved_users_personal_details,
            'funds_for_all_users':funds_for_all_user,
            'zipped_data': zip(approved_users_personal_details, funds_for_all_user),
            'zipped_data_2': zip(applied_users_personal_details, status_for_all_user),
            'zipped_data_3':zip(disbursed_users_personal_details,status_for_all_disbursed)

        }
        )



@staff_member_required
def list_of_applicants(request):
    owner = OwnerDetails.objects.last
    application = Application.objects.last()
    applied_user_ids = UploadedDocuments.objects.filter( application=application).values_list('user_id', flat=True)
    applied_users_personal_details = PersonalDetails.objects.filter(user_id__in=applied_user_ids)

    status_for_all_user = UploadedDocuments.objects.filter(user_id__in=applied_user_ids)


    applicants_count = UploadedDocuments.objects.filter(application=application).count()

    print(applied_users_personal_details)
    return render(request, 'users/list_of_applicant.html',{
        'zipped':zip(applied_users_personal_details,status_for_all_user),
        'owner':owner,
        'applicants_count':applicants_count
        })


@staff_member_required
def orphans_or_disability(request):
    owner = OwnerDetails.objects.last()
    application = Application.objects.last()
    applied_user_ids = UploadedDocuments.objects.filter(application=application).values_list('user_id', flat=True)

    applied_disable_users = AdditionalInformation.objects.filter(user_id__in=applied_user_ids).exclude(disability='No').values_list('user_id', flat=True)
    status_for_all_user = UploadedDocuments.objects.filter(user_id__in=applied_user_ids)
    personal_details_for_disable = PersonalDetails.objects.filter(user_id__in=applied_disable_users)
    applicants_count = applied_disable_users.count()


    # Get the user IDs of applicants who are orphans
    applicant_who_are_orphans = FamilyBackaground.objects.filter(user_id__in=applied_user_ids).exclude(family_status__in=['both_parents_alive', 'single_parent']).values_list('user_id', flat=True)
    status_for_orphan_applicants = UploadedDocuments.objects.filter(user_id__in=applicant_who_are_orphans)
    personal_details_for_orphans = PersonalDetails.objects.filter(user_id__in=applicant_who_are_orphans)
    count_orphans = applicant_who_are_orphans.count()


    print(applied_disable_users)
    return render(request, 'users/list_of_disable_or_orphans_applicant.html',{
        'zipped':zip(personal_details_for_disable,status_for_all_user,),
        'zipped2':zip(personal_details_for_orphans,status_for_orphan_applicants,),
        'owner':owner,
        'applicants_count':applicants_count,
        'count_orphans':count_orphans
        })


@login_required
def update_additional_info(request): 
    if request.method=='POST':
        reason = request.POST['reason']
        prev_bursary = request.POST['prev_bursary']
        org_bursary = request.POST['org_bursary']
        disability = request.POST['disability']
        chronic_illness = request.POST['chronic_illness']
        fam_disability = request.POST['fam_disability']
        fam_chronic_illness = request.POST['fam_chronic_illness']
        fund_secondary = request.POST['fund_secondary']
        fund_college = request.POST['fund_college']
        fund_uni = request.POST['fund_uni']
        other_fund_secondary = request.POST['other_fund_secondary']
        other_fund_college = request.POST['other_fund_college']
        other_fund_uni = request.POST['other_fund_uni']
        user=request.user,

        if prev_bursary == '':
            prev_bursary = "Not Received"

        if org_bursary == '':
            org_bursary = "Not Received"

        if disability == '':
            disability = "No"

        if chronic_illness == '':
            chronic_illness = "No"

        if fam_disability == '':
            fam_disability = "No"

        if fam_chronic_illness == '':
            fam_chronic_illness = "No"

        updating = AdditionalInformation.objects.filter(user=request.user).update(
            user=request.user,
            reason=reason,
            prev_bursary = prev_bursary,
            org_bursary = org_bursary,
            disability = disability,
            chronic_illness = chronic_illness,
            fam_disability = fam_disability,
            fam_chronic_illness = fam_chronic_illness,
            fund_secondary = fund_secondary,
            fund_college = fund_college,
            fund_uni = fund_uni,
            other_fund_secondary = other_fund_secondary,
            other_fund_college = other_fund_college,
            other_fund_uni = other_fund_uni
        )
        print(updating)
        if updating:
            print(updating)
            return redirect('academic_performance')

        else:
            print('not updated')
            return redirect('update_additional_info')


        
    else:
        owner = OwnerDetails.objects.first()
        try:
            additional_info = AdditionalInformation.objects.get(user=request.user)
            # print(request.user)
            return render(request, 'users/additional_info_update.html',{"owner":owner,'additional_info':additional_info})
        except AdditionalInformation.DoesNotExist:
            additional_info = AdditionalInformation.objects.filter(user=request.user)
            # print(request.user)
            return render(request, 'users/additional_info_update.html',{"owner":owner,'additional_info':additional_info})



@staff_member_required
def user_profile(request, user_id):
    user1 = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        application_status = request.POST['application_status']
        funds_for = request.POST['funds_for']
        awarded = request.POST['awarded']
        
        
        
        

        uploaded_docs = UploadedDocuments.objects.filter(user=user1).first()
        if awarded == '':
            awarded = uploaded_docs.awarded

        if uploaded_docs:
            uploaded_docs.application_status = application_status
            uploaded_docs.funds_for = funds_for
            uploaded_docs.awarded = awarded
            uploaded_docs.approved_by = request.user.first_name + ' '+request.user.last_name
            uploaded_docs.save()

            messages.info(request, f"Applicant: {user1.first_name} {user1.last_name}'s Status has been updated to {application_status}")
            return redirect('staff_dashboard')
        else:
            messages.error(request, "UploadedDocuments not found.")
            return redirect('staff_dashboard')

    else:
        # Retrieve other user-related data
        personal_details = PersonalDetails.objects.get(user=user1)
        owner = OwnerDetails.objects.last()
        family_background = FamilyBackaground.objects.get(user=user1)
        siblings = Sibling.objects.filter(user=user1)
        additional_info = AdditionalInformation.objects.get(user=user1)
        academic_performance = AcademicPerformance.objects.get(user=user1)

        try:
            uploaded_docs = UploadedDocuments.objects.filter(user=user1).first()
        except UploadedDocuments.DoesNotExist:
            # uploaded_docs = None  # Set uploaded_docs to None when no instance is found
            uploaded_docs = UploadedDocuments.objects.get(user=user1)

            


        return render(
            request, 'users/user_profile.html',
            {
                'user': user1,
                'personal_details': personal_details,
                'owner': owner,
                'family_background': family_background,
                'siblings': siblings,
                'additional_info': additional_info,
                'academic_performance': academic_performance,
                'uploaded_docs': uploaded_docs
            })



@staff_member_required
def returning_applicants(request):
    current_application = Application.objects.last()
    id_current_app = current_application.id_for_reference
    # current_date = datetime.now().date()
    previous_applications = Application.objects.filter().exclude(id_for_reference=id_current_app)
    previous_and_current_applied_user_ids = UploadedDocuments.objects.filter(application__in=previous_applications).values_list('user_id', flat=True)
    current_applied_user_ids = UploadedDocuments.objects.filter(application=current_application).values_list('user_id', flat=True)

    # all_applied_user_ids = set(previous_and_current_applied_user_ids).intersection(set(current_applied_user_ids))
    common_applied_user_ids = []
    for user_id in previous_and_current_applied_user_ids:
        if user_id in current_applied_user_ids:
            common_applied_user_ids.append(user_id)

    all_applied_user_ids = set(common_applied_user_ids)
    
    
    their_profile = PersonalDetails.objects.filter(user_id__in=all_applied_user_ids)
    application_applied = UploadedDocuments.objects.filter(user_id__in=all_applied_user_ids)
    for i in application_applied:
        print(i.application)
    owner = OwnerDetails.objects.last()
    context= {
        'zipped_returning':zip(their_profile,application_applied),
        'owner':owner}
    return render(request, 'users/returning_applicants.html',context)






@login_required
def academic_performance(request):
    if request.method == "POST":
        average_performance = request.POST['average_performance']
        sent_away = request.POST['sent_away']
        no_of_weeks = request.POST['no_of_weeks']
        annual_fees = request.POST['annual_fees']
        last_sem_fees = request.POST['last_sem_fees']
        current_sem_fees = request.POST['current_sem_fees']
        next_sem_fees = request.POST['next_sem_fees']
        helb_loan = request.POST['helb_loan']
        ref_one_name = request.POST['ref_one_name']
        ref_one_address = request.POST['ref_one_address']
        ref_one_number = request.POST['ref_one_number']
        ref_two_name = request.POST['ref_two_name']
        ref_two_address = request.POST['ref_two_address']
        ref_two_number = request.POST['ref_two_number']

        if sent_away == '':
            sent_away = 'I have not been Sent Away.'

        if no_of_weeks == '':
            no_of_weeks = 0

        academic_performance = AcademicPerformance(
            user=request.user,
            average_performance = average_performance,
            sent_away = sent_away,
            no_of_weeks = no_of_weeks,
            annual_fees = annual_fees,
            last_sem_fees = last_sem_fees,
            current_sem_fees = current_sem_fees,
            next_sem_fees = next_sem_fees,
            helb_loan = helb_loan,
            ref_one_name = ref_one_name,
            ref_one_address = ref_one_address,
            ref_one_number = ref_one_number,
            ref_two_name = ref_two_name,
            ref_two_address = ref_two_address,
            ref_two_number = ref_two_number
        )

        academic_performance.save()
        return redirect('download')
    else:
        owner = OwnerDetails.objects.first()
        academic_performance_exists = AcademicPerformance.objects.filter(user=request.user).exists()
        
        if academic_performance_exists:
            return redirect('update_academic_performance')
        else:
            return render(request, 'users/academic_performance.html', {"owner": owner})
    

@login_required
def update_academic_performance(request):
    if request.method=='POST':
        average_performance = request.POST['average_performance']
        sent_away = request.POST['sent_away']
        no_of_weeks = request.POST['no_of_weeks']
        annual_fees = request.POST['annual_fees']
        last_sem_fees = request.POST['last_sem_fees']
        current_sem_fees = request.POST['current_sem_fees']
        next_sem_fees = request.POST['next_sem_fees']
        helb_loan = request.POST['helb_loan']
        ref_one_name = request.POST['ref_one_name']
        ref_one_address = request.POST['ref_one_address']
        ref_one_number = request.POST['ref_one_number']
        ref_two_name = request.POST['ref_two_name']
        ref_two_address = request.POST['ref_two_address']
        ref_two_number = request.POST['ref_two_number']

        if sent_away == '':
            sent_away = 'I have not been Sent Away.'

        if no_of_weeks == '':
            no_of_weeks = 0

        updating = AcademicPerformance.objects.filter(user=request.user).update(
            user=request.user,
            average_performance = average_performance,
            sent_away = sent_away,
            no_of_weeks = no_of_weeks,
            annual_fees = annual_fees,
            last_sem_fees = last_sem_fees,
            current_sem_fees = current_sem_fees,
            next_sem_fees = next_sem_fees,
            helb_loan = helb_loan,
            ref_one_name = ref_one_name,
            ref_one_address = ref_one_address,
            ref_one_number = ref_one_number,
            ref_two_name = ref_two_name,
            ref_two_address = ref_two_address,
            ref_two_number = ref_two_number
         )
        print(updating)
        if updating:
            print(updating)
            return redirect('download')

        else:
            print('not updated')
            return redirect('academic_performance')
    else:
        owner = OwnerDetails.objects.first() 
        academic_performance = AcademicPerformance.objects.get(user=request.user)
        return render(request, 'users/update_academic_performance.html',{"owner":owner,'academic_performance':academic_performance})


@login_required
def generate_pdf(request):
    
    try:
        owner = OwnerDetails.objects.get()
        personal_details = PersonalDetails.objects.get(user=request.user)
        family_background = FamilyBackaground.objects.get(user=request.user)
        siblings = Sibling.objects.filter(user=request.user)
        additional_info = AdditionalInformation.objects.get(user=request.user)
        academic_performance = AcademicPerformance.objects.get(user=request.user)
        application_details = Application.objects.last()  # Make sure you have the correct way to retrieve application details
        
    except (OwnerDetails.DoesNotExist, PersonalDetails.DoesNotExist, FamilyBackaground.DoesNotExist,
            Sibling.DoesNotExist, AdditionalInformation.DoesNotExist,
            AcademicPerformance.DoesNotExist, Application.DoesNotExist):
        
        messages.error(request, 'Provide all the required information, including personal details, Family Info, Additional info, and Academic Performance. Ensure the information is accurate and verifiable.')
        return redirect('students_dashboard')
    
    try:
        name_of_application = Application.objects.last().name_of_application
    except AttributeError:
        return redirect('apply')


        
    response = HttpResponse(content_type='application/pdf')
    
    user_full_name = request.user.get_full_name()  # Get the user's full name
    current_date= datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Get the current date in YYYY-MM-DD format
    current_date1= datetime.now().strftime("%Y-%m-%d, Time: %H:%M:%S")  # Get the current date in YYYY-MM-DD format
    
    filename = f"{user_full_name}_{current_date}.pdf"  # Combine user's name and date
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    class PDF(FPDF):
        def header(self):
            self.set_font('Times', 'B', 8)
            self.cell(0, 0, f'{owner.name} {name_of_application} Application Form.', 0, 1, 'R')
            self.cell(0, 0, f'Date: {current_date1}', 0, 1, 'L')
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Times', 'I', 8)
            self.cell(0, 10, 'Name of the Applicant: ' + request.user.get_full_name(), 0, 0, 'L')
            self.cell(0, 10, 'Produced By: CDF Office representing the ' + owner.name, 0, 0, 'R')

    pdf = PDF()
    pdf.add_page()
    pdf.ln(10)
    

      # Add some vertical spacing
    
    # pdf.image('static/images/overall.jpg', x=10, y=pdf.get_y(), w=10)
    image_path = 'static/images/overall.jpg'
    original_img_width = 50  # Adjust this to the original width of your image
    img_width = original_img_width / 2  # Half of the original width
    pdf.image(image_path, x=pdf.w / 2 - img_width / 2, y=pdf.get_y(), w=img_width)
    pdf.ln(20)
    pdf.set_font("Times", 'B', 22)
    pdf.cell(0, 10, f"{owner.county} Bursary", ln=True, align='C')
    pdf.set_font("Times", 'B', 8)
    pdf.cell(0, 5, f"{owner.p_o_box}, {owner.location}. TEL: {owner.phone_number}. Email:{owner.generation_email}/{owner.manager_email}", ln=True, align='C')
    
    pdf.ln(4)
    pdf.set_font("Times", 'B', 16)
    pdf.cell(0, 10, "PART A: INSTRUCTION", ln=True, align='L')
    application_details = Application.objects.last()
    end_date_formatted = date(application_details.end_date, "F d, Y")

    content = (
        "1. The constituency bursary scheme has limited available funds and is meant to support only the very needy cases.\n"
        "   \tPersons who are able are not expected to apply.\n"
        "2. It is an offense to give false information and once discovered will lead to disqualification.\n"
        "3. Total and Partial orphans MUST present supporting documents from the area chief or Religious Leader.\n"
        "4. All forms shall be uploaded to {0} Online CDF Application Portal not later than {t}.\n"
        "\t\t\t\tNB: Any form returned after the stipulated period shall not be accepted whatsoever.\n"
        "5. Successful applicants will have the awarded bursary paid directly to university or college.\n"
        "6. All information provided will be verified with the relevant Authority(s).\n"
        "7. Applicants must upload the completed form along with supporting documents to the {0} CDF Portal."
    ).format(owner.name, t=end_date_formatted)

    pdf.set_font("Times", size=10)
    lines = content.split('\n')
    for line in lines:
        if "\t\t\t\tNB" in line:
            pdf.set_text_color(255, 0, 0)  # Set text color to red for the specific line
            pdf.multi_cell(0, 5, line)  # Print the line in red
            pdf.set_text_color(0, 0, 0)  # Reset text color to black
        else:
            pdf.multi_cell(0, 5, line)  # Print other lines in default black color

    # response.write(pdf.output(dest='S').encode('latin1'))
    pdf.ln(10)
    pdf.set_font("Times", 'B', 16)
    pdf.cell(0, 10, "PART B: TO BE FILLED BY THE APPLICANT / PARENT / GUARDIAN", ln=True, align='L')
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "i. Personal, Institutional and Other Details", ln=True, align='L')
    pdf.set_font("Times",size=12)
    pdf.multi_cell(0, 6, f"NAME OF STUDENT (AS IT APPEARS IN ID/OFFICIAL DOCUMENTS):\t\t\t\t.....{personal_details.fullname}.....", align='L')
    pdf.multi_cell(0, 6, f"GENDER:.....{personal_details.gender}.....", align='L')
   # Row layout for "DATE OF BIRTH" and "ID number"
    pdf.cell(0, 6, f"DATE OF BIRTH:.....{personal_details.date_of_birth}.....", 0, 0)  # Add "DATE OF BIRTH" in the first cell of the row
    pdf.cell(-100) 
    pdf.cell(0, 6, f"ID number:.....{personal_details.id_or_passport_no}.....", 0, 1)  # Add "ID number" in the second cell of the row
    
    pdf.multi_cell(0, 6, f"NAME OF SCHOOL /COLLEGE / UNIVERSITY:.....{personal_details.institution}.....", align='L')
    pdf.multi_cell(0, 6, f"ADMISSION/REGISTRATION NUMBER:.....{personal_details.admin_no}.....", align='L')
    pdf.multi_cell(0, 6, f"CAMPUS/ BRANCH: (for tertiary institution and University).....{personal_details.campus_or_branch}.....", align='L')
    pdf.multi_cell(0, 6, f"FACULTY/ DEPARTMENT: (for tertiary institution and University).....{personal_details.faculty}.....", align='L')
    pdf.multi_cell(0, 6, f"COURSE OF STUDY: (for tertiary institution and University.....{personal_details.course}.....", align='L')
    pdf.multi_cell(0, 6, f"MODE OF STUDY:.....{personal_details.mode_of_study}.....", align='L')
    pdf.cell(0, 6, f"CLASS/GRADE/YEAR OF STUDY:.....{personal_details.year_of_study}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"COURSE DURATION:.....{personal_details.course_duration}.....", 0, 1)
    pdf.multi_cell(0, 6, f"EXPECTED YEAR AND MONTH OF COMPLETION:.....{personal_details.year_of_completion}.....", align='L')
    pdf.multi_cell(0, 6, f"MOBILE/TELEPHONE NUMBER:.....{personal_details.mobile_no}.....", align='L')
    pdf.cell(0, 6, f"POLLING STATION:.....{personal_details.name_polling_station}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"WARD:.....{personal_details.ward}.....", 0, 1)
    pdf.cell(0, 6, f"LOCATION:.....{personal_details.location}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"SUB LOCATION:.....{personal_details.sub_location}.....", 0, 1)
    pdf.multi_cell(0, 6, f"PHYSICAL ADDRESS:.....{personal_details.physical_address}.....", align='L')
    pdf.multi_cell(0, 6, f"PERMANENT ADDRESS:.....{personal_details.permanent_address}.....", align='L')
    pdf.multi_cell(0, 6, f"INSTITUTION'S POSTAL ADDRESS:.....{personal_details.institution_postal_address}.....", align='L')
    pdf.multi_cell(0, 6, f"INSTITUTION'S TELEPHONE NUMBER:.....{personal_details.institution_telephone_no}.....", align='L')
    pdf.multi_cell(0, 8, f"AMOUNT APPLIED FOR (Kshs):.....{personal_details.ammount_requesting}.....", align='L')
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 8, "(Attach support documents including letter of admission, fees structure and recommendations)", ln=True, align='L')
    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "ii. FAMILY BACKGROUND", ln=True, align='L')
    pdf.set_font("Times",size=12)
     # Replace underscores with spaces and convert to title case
    family_status_text = " ".join(word.title() for word in family_background.family_status.split("_"))
    
    # Print the modified text
    pdf.multi_cell(0, 6, f"Kindly indicate your family status:.....{family_status_text}.....", align='L')
    pdf.multi_cell(0, 6, f"Number of siblings ( alive):.....{family_background.number_siblings}.....", align='L')
    pdf.multi_cell(0, 6, f"Estimated Family income:.....{family_background.family_income}.....(annually Kshs.)", align='L')
    pdf.multi_cell(0, 6, f"Estimated Family expense:.....{family_background.family_expense}.....(annually Kshs.)", align='L')
    pdf.multi_cell(0, 8, "Attach support documents eg- death certificate / a verification letter from area chief/sub chief", align='L')
    pdf.ln(4)
    pdf.multi_cell(0, 6, f"a) Father", align='L')
    pdf.cell(0, 6, f"Full Name:.....{family_background.father_name}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"Address:.....{family_background.father_address}.....", 0, 1)
    pdf.cell(0, 6, f"Telephone Number:.....{family_background.father_mobile_no}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"Occupation:.....{family_background.father_occupation}.....", 0, 1)
    father_employment = " ".join(word.title() for word in family_background.father_type_of_employment.split("_"))
    pdf.multi_cell(0, 6, f"Type of employment:.....{father_employment}.....", align='L')
    pdf.multi_cell(0, 6, f"Main source of income:.....{family_background.father_main_source_of_income}.....", align='L')
    pdf.ln(4)
    pdf.multi_cell(0, 6, f"b) Mother", align='L')
    pdf.cell(0, 6, f"Full Name:.....{family_background.mother_full_name}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"Address:.....{family_background.mother_address}.....", 0, 1)
    pdf.cell(0, 6, f"Telephone Number:.....{family_background.mother_telephone_number}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"Occupation:.....{family_background.mother_occupation}.....", 0, 1)
    mother_employment = " ".join(word.title() for word in family_background.mother_type_of_employment.split("_"))
    pdf.multi_cell(0, 6, f"Type of employment:.....{mother_employment}.....", align='L')
    pdf.multi_cell(0, 6, f"Main source of income:.....{family_background.mother_main_source_of_income}.....", align='L')
    pdf.ln(4)
    pdf.multi_cell(0, 6, f"c) Guardian", align='L')
    pdf.cell(0, 6, f"Full Name:.....{family_background.guardian_full_name}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"Address:.....{family_background.guardian_address}.....", 0, 1)
    pdf.cell(0, 6, f"Telephone Number:.....{family_background.guardian_telephone_number}.....", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, f"Occupation:.....{family_background.guardian_occupation}.....", 0, 1)
    guardian_employment = " ".join(word.title() for word in family_background.guardian_type_of_employment.split("_"))
    pdf.multi_cell(0, 6, f"Type of employment:.....{guardian_employment}.....", align='L')
    pdf.multi_cell(0, 6, f"Main source of income:.....{family_background.guardian_main_source_of_income}.....", align='L')
    
    # SIBLINGS
    # Split data into two columns
    pdf.ln(4)
    pdf.cell(0, 6, "d) Provide the names of siblings in school/ college/ university this year in the table below ", 0, 1)

    data = (
        "S/No., Name, Institution, Annual fees payable (Kshs.)\n"
        # ... (remaining data)
    )
    i=1
    for sibling in siblings:
        first_two_names = " ".join(sibling.sibling_name.split()[:2])
        data += f"{i}, {first_two_names}, {sibling.institution}, {sibling.fees}\n"
        i+=1
    

    column_width = pdf.w / 2 - 15  # Width of each column
    lines = data.split('\n')  # Split the data into lines
    
    # Start position for the first column
    pdf.set_xy(10, pdf.get_y())
    
    for line in lines:
        pdf.cell(1)
        items = line.split(', ')
        for item in items:
            pdf.cell(48.8, 5, item, 1)
        pdf.ln()  # Move to the next row
    

    #additional Info
    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "iii. APPLICANT'S ADDITIONAL INFORMATION", ln=True, align='L')
    pdf.set_font("Times",size=12)
    pdf.multi_cell(0, 6, f"a). Why are you applying for bursary assistance?.....{additional_info.reason}.....", align='L')
    pdf.multi_cell(0, 6, f"b). Have you received any financial support / bursaries from NG-CDF in the past?.....{additional_info.prev_bursary}.....", align='L')
    pdf.multi_cell(0, 6, f"c). Have you received any financial support bursaries from other organizations in the past?.....{additional_info.org_bursary}.....", align='L')
    pdf.multi_cell(0, 6, f"d). Do you suffer from any physical impairment (disability) ?.....{additional_info.disability}.....", align='L')
    pdf.multi_cell(0, 6, f"e). Do you suffer from any chronic illness?.....{additional_info.chronic_illness}.....", align='L')
    pdf.multi_cell(0, 6, f"f). Do your parents/guardians have any form of disability?.....{additional_info.fam_disability}.....", align='L')
    pdf.multi_cell(0, 6, f"g). Do your parents/guardians suffer from any chronic illness?.....{additional_info.fam_chronic_illness}.....", align='L')
    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "EDUCATION FUNDING HISTORY", ln=True, align='L')
    pdf.set_font("Times", size=12)

    pdf.cell(0, 7, "i). State the main source of funding for your education in the past as below:", ln=True, align='L')
    pdf.multi_cell(0, 6, f"In secondary school.....{additional_info.fund_secondary}.....", align='L')
    pdf.multi_cell(0, 6, f"In college.....{additional_info.fund_college}.....", align='L')
    pdf.multi_cell(0, 6, f"In the university.....{additional_info.fund_uni}.....", align='L')

    pdf.cell(0, 7, "ii). Indicate other sources of funding if any:", ln=True, align='L')
    pdf.multi_cell(0, 6, f"In secondary school.....{additional_info.other_fund_secondary}.....", align='L')
    pdf.multi_cell(0, 6, f"In college.....{additional_info.other_fund_college}.....", align='L')
    pdf.multi_cell(0, 6, f"In the university.....{additional_info.other_fund_uni}.....", align='L')

    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "APPLICANT'S ACADEMIC PERFORMANCE", ln=True, align='L')
    pdf.set_font("Times", size=12)

    academic_per = " ".join(word.title() for word in academic_performance.average_performance.split("_"))
    pdf.multi_cell(0, 6, f"a). What is your average academic performance?.....{academic_per}.....", align='L')
    pdf.multi_cell(0, 6, f"b). Have you been sent away from school?.....{academic_performance.sent_away}.....", align='L')
    pdf.multi_cell(0, 6, f"c). Specify the number of weeks you stayed away from school.....{academic_performance.no_of_weeks}.....", align='L')
    pdf.multi_cell(0, 6, f"d). Annual fees as per fees structure Kshs.....{academic_performance.annual_fees}.....", align='L')
    pdf.multi_cell(0, 6, f"e). Last semester's/Term's fee balance Kshs.....{academic_performance.last_sem_fees}.....", align='L')
    pdf.multi_cell(0, 6, f"f). This semester's/Term's fee balance Kshs.....{academic_performance.current_sem_fees}.....", align='L')
    pdf.multi_cell(0, 6, f"g). Next semester's/Term's fee balance Kshs.....{academic_performance.next_sem_fees}.....", align='L')
    pdf.multi_cell(0, 6, f"h). Loan from HELB ( where applicable).....{academic_performance.helb_loan}.....", align='L')
    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "REFEREES", ln=True, align='L')
    pdf.set_font("Times", size=12)
    pdf.multi_cell(0, 7, "The student/parent/guardian should provide the names and telephone contacts of at least two referees who \nknow the family well", align='L')
    pdf.ln(4)
    pdf.multi_cell(0, 6, f"1). Name.....{academic_performance.ref_one_name}.....", align='L')
    pdf.multi_cell(0, 6, f"    Address.....{academic_performance.ref_one_address}.....", align='L')
    pdf.multi_cell(0, 6, f"    Telephone no.....{academic_performance.ref_one_number}.....", align='L')
    pdf.ln(4)

    pdf.multi_cell(0, 6, f"2). Name.....{academic_performance.ref_two_name}.....", align='L')
    pdf.multi_cell(0, 6, f"    Address.....{academic_performance.ref_two_address}.....", align='L')
    pdf.multi_cell(0, 6, f"    Telephone no.....{academic_performance.ref_two_number}.....", align='L')
    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "PART C: DECLARATIONS", ln=True, align='L')
    pdf.cell(0, 10, "(1) STUDENT'S DECLARATION", ln=True, align='L')
    pdf.set_font("Times", size=12)
    pdf.cell(0, 6, "I declare that I have read this form/ this form has been read to me and I hereby confirm that the", ln=True, align='L')
    pdf.cell(0, 6, "information given herein is true to the best of my knowledge and belief; I understand that any false", ln=True, align='L')
    pdf.cell(0, 6, "information provided shall lead to my automatic disqualification by the committee.", ln=True, align='L')
    pdf.ln(5)
    pdf.cell(0, 6, "Student's Signature:........................................", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, "Date:.......................", 0, 1)
    
    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "(2) PARENT'S / GUARDIAN'S DECLARATION", ln=True, align='L')
    pdf.set_font("Times", size=12)
    pdf.cell(0, 6, "I declare that I have read this form/ this form has been read to me and I hereby confirm that the ", ln=True, align='L')
    pdf.cell(0, 6, "information given herein is true to the best of my knowledge and belief; I understand that any false", ln=True, align='L')
    pdf.cell(0, 6, "information provided shall lead to disqualification of the student by the committee.", ln=True, align='L')
    pdf.ln(5)
    pdf.cell(0, 6, "Parent's /Guardian's Name:............................................  Date.....................", 0, 0)
    pdf.cell(-50)
    pdf.cell(0, 6, "Sign:.......................", 0, 1)
    

    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "PART D: VERIFICATIONS", ln=True, align='L')
    pdf.set_font("Times", size=12)
    pdf.cell(0, 6, "Verified by:", ln=True, align='L')

    pdf.cell(0, 6, "a). Religious leader :",ln=True, align='L')
    pdf.cell(0, 6, "Name of religion:...................................................................................",ln=True, align='L')
    pdf.cell(0, 6, "Type of religion: Christian ( ) Muslim ( ) Hindu ( ) Any other ( ) (tick appropriately)",ln=True, align='L')
    pdf.cell(0, 6, "If other specify....................................................................................",ln=True, align='L')
    pdf.ln(2)
    pdf.multi_cell(0, 6, "Comment on the status of the family / parents of the applicant............................................................\n................................................................................................................................................................\n.......................................................................", 0, 0)
    pdf.ln(2)
    pdf.cell(0, 6, "I CERTIFY THAT THE INFORMATION GIVEN HEREIN IS TRUE",ln=True, align='L')
    pdf.ln(3)
    pdf.cell(0, 6, "NAME:............................................  SIGNATURE.....................", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "DATE & OFFICIAL STAMP:.......................", 0, 1)

    pdf.ln(10)
    pdf.cell(0, 6, "b). Chief / Assistant chief:",ln=True, align='L')
    pdf.cell(0, 6, "Name of the area chief / Assistant chief:....................................................................",ln=True, align='L')
    pdf.cell(0, 6, "Location / sub location:................................................................................................",ln=True, align='L')
    pdf.ln(2)
    pdf.multi_cell(0, 6, "Comment on the status of the family / parents of the applicant............................................................\n................................................................................................................................................................\n.......................................................................", 0, 0)
    pdf.ln(2)
    pdf.cell(0, 6, "I CERTIFY THAT THE INFORMATION GIVEN HEREIN IS TRUE",ln=True, align='L')
    pdf.ln(3)
    pdf.cell(0, 6, "SIGNATURE................................................", 0, 0)
    pdf.cell(-100)
    pdf.cell(0, 6, "DATE & OFFICIAL STAMP:.......................", 0, 1)


    pdf.ln(20)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "PART E: FOR OFFICIAL USE BY THE POLLING STATION VETTING COMMITTEE", ln=True, align='L')
    pdf.set_font("Times", 'B', size=12)
    pdf.ln(4)
    pdf.cell(0, 6, "This form was dully filled and signed:             Yes (  )         No (  )",ln=True, align='L')
    pdf.ln(3)
    pdf.cell(0, 6, "All support documents hav been attached:      Yes (  )         No (  )",ln=True, align='L')
    pdf.set_font("Times", size=12)
    pdf.ln(3)
    pdf.cell(0, 6, "Recommended for Bursary:                                 Yes (  )         No (  )",ln=True, align='L')
    pdf.ln(3)
    pdf.cell(120)
    pdf.multi_cell(0, 6, "Reasons for non recommendation\n:...................................................\n..................................................", 0, 1)


    pdf.ln(10)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "Polling station vetting committee members", ln=True, align='L')
    pdf.set_font("Times", size=12)
    pdf.ln(3)
    pdf.cell(0, 6, "Chairperson's Name:........................................  Date.....................", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "Signature:.......................", 0, 1)
    pdf.ln(3)
    pdf.cell(0, 6, "Secretary's Name:............................................  Date.....................", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "Signature:.......................", 0, 1)
    pdf.ln(3)
    pdf.cell(0, 6, "Member Name:............................................  Date.....................", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "Signature:.......................", 0, 1)

    pdf.ln(8)
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, "PART F: FOR OFFICIAL USE BY THE CONSTTTUENCY EDUCATION BURSARY SUB COMMITTEE", ln=True, align='L')
    pdf.set_font("Times", size=12)
    pdf.ln(3)
    pdf.cell(0, 6, "Recommended for Bursary award     (  ) ", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "Not recommended for Bursary award     (  ) ", 0, 1)

    pdf.ln(8)
    pdf.cell(0, 6, "Bursary awarded Kshs....................... ", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "Reasons....................................................... ", 0, 1)

    pdf.ln(8)
    pdf.cell(0, 6, "Secretary's Name....................................... ", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "...................................................................................", 0, 1)
    pdf.ln(8)
    pdf.cell(0, 6, "Date.......................         Signature............................  ", 0, 0)
    pdf.cell(-80)
    pdf.cell(0, 6, "STAMP ....................................", 0, 1)




        # Add context 3
    pdf.ln(10)  # Add vertical spacing
    pdf.set_font("Times", size=12, style='B')  # Set font size to 12 and bold for the context title
    pdf.cell(0, 6, "KEY ATTACHMENTS TO THE FORM", ln=True)
    pdf.cell(0, 6, "Applicants MUST attach copies of the relevant documents including the following: ", ln=True)
    pdf.set_font("Times", size=10)  # Reset font size and style
    supporting_documents = (
        "1. Students' transcript/ Report Form\n"
        "2. Photocopy of parents' / guardians National Identity Card\n"
        "3. Photocopy of students' National Identity Card (mandatory for post school students)\n"
        "4. Photocopy of birth certificate\n"
        "5. Photocopy of the secondary/ college / university ID card\n"
        "6. Parents death certificate / burial permit (mandatory for orphans)\n"
        "7. Current fees structure (mandatory for all applicants)\n"
        "8. Admission letters (mandatory for colleges and universities)"
    )
    pdf.multi_cell(0, 5, supporting_documents)

    response.write(pdf.output(dest='S').encode('latin1'))
    return response

@login_required
def apply(request):
    if request.method=='POST':
        user = request.user
        
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        transcript_report_form = request.FILES.get('transcript_report_form')
        parents_guardians_id_card = request.FILES.get('parents_guardians_id_card')
        students_id_card = request.FILES.get('students_id_card')
        id_card_birth_certificate = request.FILES.get('id_card_birth_certificate')
        parents_death_certificate = request.FILES.get('parents_death_certificate')
        fees_structure = request.FILES.get('fees_structure')
        admission_letters = request.FILES.get('admission_letters')
        verification_document = request.FILES.get('verification_document')
        uploaded_documents = UploadedDocuments(
            user=user,
            application=Application.objects.last(),
            
            transcript_report_form=transcript_report_form,
            parents_guardians_id_card=parents_guardians_id_card,
            students_id_card=students_id_card,
            id_card_birth_certificate=id_card_birth_certificate,
            parents_death_certificate=parents_death_certificate,
            fees_structure=fees_structure,
            admission_letters=admission_letters,
            verification_document=verification_document,
        )
        saving = uploaded_documents.save()
        last_application = Application.objects.last()
        
        if last_application:
            last_application = Application.objects.filter(id_for_reference= last_application.id_for_reference).update(
                number_of_applicant = last_application.number_of_applicant + 1
            )
            print('added')          
        else:

            print('not added')
        try:
            saving = UploadedDocuments.objects.get(user=request.user)
        except UploadedDocuments.DoesNotExist:
            saving = None

        if saving:
            # owner = OwnerDetails.objects.first()
            messages.success(request, "Documents uploaded Successfully.")
            return redirect('home')
        
        else:
            return render(request, 'users/failed.html')

    else:
        owner = OwnerDetails.objects.first()
        current_date = datetime.now().date()       

        # Get the last added Application instance
        last_application = Application.objects.last()
        try:
            already = UploadedDocuments.objects.get(user=request.user,application=last_application)   

        except UploadedDocuments.DoesNotExist:
            already = None 

        try:
            level_of_Education = PersonalDetails.objects.get(user = request.user).education_level

        except PersonalDetails.DoesNotExist:
            level_of_Education = None

            
        
        if last_application:
            # Get the current date
            current_date = datetime.now().date()

            # Compare the end_date with the current date
            application_statuses = ['Approved', 'Funded', 'Disbursed']
            approved_sum_sec = UploadedDocuments.objects.filter(application_status__in=application_statuses, application=last_application,funds_for='Secondary').aggregate(Sum('awarded'))['awarded__sum']
            approved_sum_uni = UploadedDocuments.objects.filter(application_status__in=application_statuses, application=last_application,funds_for='Higher_Education').aggregate(Sum('awarded'))['awarded__sum']
            approved_sum_sec = approved_sum_sec = int(approved_sum_sec) if approved_sum_sec is not None else 0
            approved_sum_uni = approved_sum_uni = int(approved_sum_uni) if approved_sum_uni is not None else 0
            # all_funds = int(last_application.funds_available_for_secondary_schools + last_application.funds_available_for_universities)
            print(f"Funds funds_available_for_secondary_schools ..... {last_application.funds_available_for_secondary_schools}")

            if last_application.end_date > current_date and last_application.is_active:
                # The end_date has passed
                print("The end date has not passed.")
                if already is None:
                    owner = OwnerDetails.objects.first()
                    if level_of_Education == 'Secondary':
                        if approved_sum_sec < last_application.funds_available_for_secondary_schools:
                            return render(request, 'users/uploading.html',{'owner':owner,'last_application':last_application})
                        else:
                            context={
                            'message':f"Applications for {level_of_Education} Schools Funds has been Suspended.",
                            'owner':owner,
                            }
                            return render(request, 'users/404.html',context)
                    else:
                        if approved_sum_uni < last_application.funds_available_for_universities:
                            return render(request, 'users/uploading.html',{'owner':owner,'last_application':last_application})
                        else:
                            context={
                            'message':"Applications for Higher Education Fund has been Suspended.",
                            'owner':owner,
                            }
                            return render(request, 'users/404.html',context)
                           

                else:
                    # return HttpResponse(f'You have already applied and your application status: {already.application_status}')
                    status = already.application_status
                    owner = OwnerDetails.objects.last()
                    return render(request, 'users/submitted.html', {'status':status,'owner':owner})
                

            else:
                # The end_date has not passed
                print("The end date has passed.")
                context={
                'message':"Deadline for Submission has passed or Application has been Suspended.",
                'owner':owner,
                }
                return render(request, 'users/404.html',context)
                # return HttpResponse(f'You passed the deadline which was {last_application.end_date}')
        else:
            # No Application instance exists
            print("No Application instance found.")
            context={
                'message':"No Application Open",
                'owner':owner,
            }
            return render(request, 'users/404.html',context)
        


@staff_member_required
def generate_bursary_letter(request, user_id):
    user1 = get_object_or_404(User, pk=user_id)
    personal_details = PersonalDetails.objects.get(user=user1)
    last_application = Application.objects.last()
    owner = OwnerDetails.objects.last()
    uploaded = UploadedDocuments.objects.filter(user=user1).first()

    recipient_name = personal_details.fullname
    institution_name = personal_details.institution
    amount_awarded = uploaded.awarded
    course_name = personal_details.course
    Constituency_Name = owner.name


    current_date_formatted = date(datetime.now(), "F d, Y")

    UploadedDocuments.objects.filter(user=user1,application=last_application).update(
        application_status = 'Disbursed'
    )

    if personal_details.gender == 'male':
        pronoun = 'his'
    else:
        pronoun = 'her'

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Times", 'B', size=10)

        # Specify the image path and original width
    image_path = 'static/images/overall.jpg'
    original_img_width = 50  # Adjust this to the original width of your image

    # Calculate the new width for the image (e.g., half of the original width)
    img_width = original_img_width / 2

    # Set the x-coordinate to push the image to the left side (e.g., x=10 for a 10-unit margin)
    pdf.image(image_path, x=10, y=pdf.get_y(), w=img_width)


    # pdf.cell(0, 8, f"Date: {current_date}", ln=True, align="R")
    pdf.cell(0, 4, f"NG Constituency Development Fund Committee", ln=True, align="R")
    pdf.cell(0, 4, f"{Constituency_Name}", ln=True, align="R")
    pdf.cell(0, 4, f"{owner.location}", ln=True, align="R")
    pdf.multi_cell(0, 4, f"{owner.p_o_box}, {owner.p_o_box_location}", align="R")
    pdf.multi_cell(0, 4, f"Tel: {owner.phone_number}", align="R")
    pdf.multi_cell(0, 4, f"Email:{owner.generation_email} / {owner.manager_email}", align="R")
    pdf.ln(4)
    pdf.cell(0, 4, f"{owner.county}",ln=True, align="L")
    pdf.ln(4)
   
    pdf.set_line_width(2)

    # Define the starting X and Y coordinates for the line
    x1 = 10  # 20px from the left margin
    x2 = pdf.w - 10  # 20px from the right margin
    y = pdf.get_y()  # Maintain the current Y position

    # Draw a horizontal line by drawing a line
    pdf.line(x1, y, x2, y)
    pdf.set_line_width(0.5)
    pdf.ln(4)

    pdf.cell(0, 4, f"REF:..................................................................................................", align="L")
    pdf.cell(0, 4, f"{current_date_formatted}", ln=True, align="R")


    pdf.ln(6)
    pdf.cell(0, 5.5, f"The Finance Department,", ln=True, align="L")
    pdf.cell(0, 5.5, f"{personal_details.institution},", ln=True, align="L")
    pdf.cell(0, 5.5, f"P. O. Box: {personal_details.institution_postal_address},", ln=True, align="L")

    
    pdf.ln(5)
    pdf.set_font("Times", 'B', size=12)

    pdf.cell(0,6, "Dear Sir/Madam,", ln=True, align="L")
    pdf.ln(3)

    pdf.set_font("Times", 'B', size=12)

    pdf.multi_cell(0, 8, f"RE: Notification of Bursary Award for {recipient_name} of Admission/Registration No. {personal_details.admin_no} - {course_name}.")
    pdf.ln(3)
    pdf.set_font("Times", size=12)

    letter_content = (
        f"I hope this letter finds you in good health. I am writing to inform you about a significant "
        f"development regarding one of your esteemed students. It is with great pleasure that I convey the news "
        f"that {recipient_name}, a student of {course_name} at {institution_name}, has been awarded a bursary of "
        f"Kshs. {amount_awarded} under the {Constituency_Name}, Constituency Development Fund (CDF) scheme.\n\n"
        f"The {Constituency_Name} CDF has recognized {recipient_name}'s dedication and commitment to {pronoun} "
        f"education, as well as {pronoun} exceptional academic achievements. After a thorough evaluation process, "
        f"{recipient_name} has been selected as a deserving recipient of this prestigious bursary.\n\n"
        f"The bursary award aims to provide financial assistance to students who demonstrate exemplary academic "
        f"performance and a strong commitment to their studies. It serves as a testament to {recipient_name}'s hard "
        f"work, dedication, and potential to contribute positively to {pronoun} field of study and society as a whole.\n\n"
        f"We kindly request your cooperation in notifying {recipient_name} about this significant achievement. We "
        f"believe that your institution's recognition and support will further motivate {recipient_name} to excel "
        f"academically and contribute to the institution's reputation.\n\n"
        f"We look forward to {recipient_name}'s continued success and academic accomplishments. Once again, please "
        f"accept our warm congratulations on this remarkable achievement.\n\n"
        f"If you require any further information or documentation related to the bursary award, please do not "
        f"hesitate to contact our office.\n\n"
    )

    pdf.multi_cell(0, 5, letter_content)

    pdf.cell(0,6, "Thank you for your co-operation.")
    pdf.ln(10)
    pdf.cell(0,6,"Yours's Faithfully,")
    pdf.ln(15)
    pdf.cell(0,6,f"{owner.name_of_the_chairperson},", ln=True)
   
    pdf.cell(0,6,"CDF Chairperson.", ln=True)

    pdf.cell(0,6,f"{owner.name}.", ln=True)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Bursary_Award_Letter-{recipient_name}.pdf"'
    response.write(pdf.output(dest='S').encode('latin1'))
    return response




@staff_member_required
def new_application(request):
    if request.method=='POST':
        id_for_reference = request.POST['id_for_reference']
        name_of_application = request.POST['name_of_application']
        funds_available_for_secondary_schools = request.POST['funds_available_for_secondary_schools']
        funds_available_for_universities = request.POST['funds_available_for_universities']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        is_active = request.POST['activation']
        if is_active == 'Yes':
            is_active = True
        else:
            is_active = False

        if Application.objects.filter(id_for_reference=id_for_reference):
            messages.error(request, f"Application with ID {id_for_reference} already exists. Try again!")
            return redirect('new_application')

        application = Application(
            id_for_reference = id_for_reference,
            name_of_application = name_of_application,
            funds_available_for_secondary_schools = funds_available_for_secondary_schools,
            funds_available_for_universities = funds_available_for_universities,
            start_date = start_date,
            end_date = end_date,
            is_active = is_active
        )

        application.save()
        messages.info(request, f'New Application Has Been Created under {name_of_application}')
        return redirect('staff_dashboard')
    else:

        owner = OwnerDetails.objects.last()
        current_application = Application.objects.last()
        context = {
            'current_application' : current_application,
            'owner':owner,

        }
        return render(request, 'users/new_application.html',context)


@staff_member_required
def update_current_application(request):
    if request.method=='POST':
        id_for_reference = request.POST['id_for_reference']
        name_of_application = request.POST['name_of_application']
        funds_available_for_secondary_schools = request.POST['funds_available_for_secondary_schools']
        funds_available_for_universities = request.POST['funds_available_for_universities']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        is_active = request.POST['activation']
        

        application =Application.objects.filter(id_for_reference= id_for_reference).update(
            id_for_reference = id_for_reference,
            name_of_application = name_of_application,
            funds_available_for_secondary_schools = funds_available_for_secondary_schools,
            funds_available_for_universities = funds_available_for_universities,
            start_date = start_date,
            end_date = end_date,
            is_active = is_active
        )
        messages.info(request, 'Current Application Has Been Updated.')
        return redirect('staff_dashboard')
    else:

        owner = OwnerDetails.objects.last()
        current_application = Application.objects.last()
        context = {
            'current_application' : current_application,
            'owner':owner,

        }
        return render(request, 'users/new_application.html',context)


################################################ ANALYSIS ##########################
@staff_member_required
def approved_lst_pdf(request):
    last_application = Application.objects.last()
    owner = OwnerDetails.objects.last()
    approved_sum = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application).aggregate(Sum('awarded'))['awarded__sum'] or 0

    # all_approved = UploadedDocuments.objects.filter(application_status='Approved', application=last_application).values_list('user_id', flat=True)
    all_disbursed_higher = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Higher_Education').values_list('user_id', flat=True)

    # approved_users_personal_details = PersonalDetails.objects.filter(user_id__in=all_approved)
    disbursed_users_personal_details = PersonalDetails.objects.filter(user_id__in=all_disbursed_higher)

    # approved_users_awarded = UploadedDocuments.objects.filter(user_id__in=all_approved)
    disbursed_users_awarded = UploadedDocuments.objects.filter(user_id__in=all_disbursed_higher)
    # Count the number of records with application_status set to 'Disbursed'
    disbursed_count = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application).count() or 0

    disbursed_sec = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for = 'Secondary').count() or 0
    disbursed_high = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for="Higher_Education").count() or 0
 
    # Now, disbursed_count contains the count of 'Disbursed' records


   
    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Times", 'B', size=10)

        # Specify the image path and original width
    image_path = 'static/images/overall.jpg'
    original_img_width = 50  # Adjust this to the original width of your image

    # Calculate the new width for the image (e.g., half of the original width)
    img_width = original_img_width / 2

    # Set the x-coordinate to push the image to the left side (e.g., x=10 for a 10-unit margin)
    pdf.image(image_path, x=10, y=pdf.get_y(), w=img_width)


    # pdf.cell(0, 8, f"Date: {current_date}", ln=True, align="R")
    pdf.cell(0, 4, f"NG Constituency Development Fund Committee", ln=True, align="R")
    pdf.cell(0, 4, f"{owner.name}", ln=True, align="R")
    pdf.cell(0, 4, f"{owner.location}", ln=True, align="R")
    pdf.multi_cell(0, 4, f"{owner.p_o_box}, {owner.p_o_box_location}", align="R")
    pdf.multi_cell(0, 4, f"Tel: {owner.phone_number}", align="R")
    pdf.multi_cell(0, 4, f"Email:{owner.generation_email} / {owner.manager_email}", align="R")
    pdf.ln(4)
    pdf.cell(0, 4, f"{owner.county}",ln=True, align="L")
    pdf.ln(4)
   
    pdf.set_line_width(2)

    # Define the starting X and Y coordinates for the line
    x1 = 10  # 20px from the left margin
    x2 = pdf.w - 10  # 20px from the right margin
    y = pdf.get_y()  # Maintain the current Y position

    # Draw a horizontal line by drawing a line
    pdf.line(x1, y, x2, y)
    pdf.set_line_width(0.5)
    pdf.ln(4)
    pdf.set_font("Arial", style='B', size=16)

    pdf.cell(0,6, f"Report of {last_application.name_of_application}", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 5, f"Education plays a pivotal role in the development of individuals and communities, serving as a catalyst for progress and empowerment. In line with this belief, the Constituency Development Fund (CDF) - {owner.name} for the year {last_application.id_for_reference} embarked on a mission to transform lives through the provision of bursaries to deserving students within our constituency. This report serves as a comprehensive account of our commitment to enhancing educational opportunities and fostering a brighter future for our youth.")
    pdf.ln(4)
    pdf.multi_cell(0,5, 'The year {fy} marked a significant milestone as the CDF allocated substantial resources, amounting to Kshs. {t:,} to support the education of students in our constituency. These bursaries aimed not only to alleviate the financial burdens of students and their families but also to empower them to pursue higher education or secondary education and achieve their dreams.'.format(fy=last_application.id_for_reference,t=last_application.funds_available_for_secondary_schools + last_application.funds_available_for_universities))
    pdf.ln(4)
    pdf.multi_cell(0,5,"This report stands as a testament to the power of education, the unwavering support of the CDF, and the resilience of our students. It is a reflection of our collective commitment to nurturing talent, fostering academic achievement, and building a brighter future for our constituency.")

    pdf.ln(4)

     # Create a table header
    pdf.set_fill_color(0, 191, 255)  # Light Blue
    pdf.set_font("Arial",  size=10)
    pdf.cell(0,6, "Overview", ln=True, align="L")
    pdf.ln(3)

    pdf.cell(115, 10, "Item", 1, 0, 'L', 1)
    pdf.cell(60, 10, "Details", 1, 1, 'L', 1)
    

    pdf.cell(115, 10, "Financial Year", 1)
    pdf.cell(60, 10, f"{last_application.id_for_reference}", 1,ln=True)

    pdf.cell(115, 10, "Commencement Date", 1)
    pdf.cell(60, 10, f"{last_application.start_date}", 1,ln=True)

    pdf.cell(115, 10, "Conclusion Date", 1)
    pdf.cell(60, 10, f"{last_application.end_date}", 1,ln=True)

##################Applicants####
    pdf.cell(115, 10, "Total Number of Applicants", 1)
    pdf.cell(60, 10, f"{last_application.number_of_applicant}", 1,ln=True)

    pdf.cell(115, 10, "Number of Applicants Approved", 1)
    pdf.cell(60, 10, f"{disbursed_count}", 1,ln=True)


#############Approved sec
    pdf.cell(115, 10, "Number of Applicants Benefited in Secondary", 1)
    pdf.cell(60, 10, f"{disbursed_sec}", 1,ln=True)
#############Approved shigh

    pdf.cell(115, 10, "Number of Applicants Benefited in Higher Education", 1)
    pdf.cell(60, 10, f"{disbursed_high}", 1,ln=True)


    pdf.cell(115, 10, "Funds Allocated for Secondary Schools", 1)
    pdf.cell(60, 10, "Kshs. {:,}".format(last_application.funds_available_for_secondary_schools), 1,ln=True)


    pdf.cell(115, 10, "Funds Allocated for Higher Education", 1)
    pdf.cell(60, 10, "Kshs. {:,}".format(last_application.funds_available_for_universities), 1,ln=True)


##################distributed
    dis_sec = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Secondary').aggregate(Sum('awarded'))['awarded__sum'] or 0
    dis_higher = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Higher_Education').aggregate(Sum('awarded'))['awarded__sum'] or 0

    pdf.cell(115, 10, "Funds Disbursed to Secondary Schools", 1)
    pdf.cell(60, 10, "Kshs. {:,}".format(dis_sec), 1,ln=True)


    pdf.cell(115, 10, "Funds Disbursed for Higher Education", 1)
    pdf.cell(60, 10, "Kshs. {:,}".format(dis_higher), 1,ln=True)


##################remaining
    remain_sec = last_application.funds_available_for_secondary_schools - dis_sec
    remain_higher = last_application.funds_available_for_universities - dis_higher
    pdf.cell(115, 10, "Remaining Funds for Secondary Schools", 1)
    pdf.cell(60, 10, "Kshs. {:,}".format(remain_sec), 1,ln=True)


    pdf.cell(115, 10, "Remaining Funds for Higher Education", 1)
    pdf.cell(60, 10, "Kshs. {:,}".format(remain_higher), 1,ln=True)



    pdf.set_font("Arial", style='B', size=12)
    pdf.ln(14)

    pdf.cell(0,6, "[i] Higher Education", ln=True, align="L")
    pdf.set_font("Arial", style='B', size=8)


    pdf.cell(9, 10, "S/No.", 1, 0, 'L', 1)
    pdf.cell(60, 10, "Name", 1, 0, 'L', 1)
    pdf.cell(15, 10, "Gender", 1, 0, 'L', 1)
    pdf.cell(80, 10, "Institution", 1, 0, 'L', 1)
    pdf.cell(20, 10, "Amount", 1, 1, 'L', 1)

    # Create a table with student details
    pdf.set_fill_color(255, 255, 255)  # White
    pdf.set_font("Arial", size=8)
    s_no = 1
    total = 0
    for student, awarded_data in zip(disbursed_users_personal_details, disbursed_users_awarded):
        pdf.cell(9, 10, str(s_no), 1)
        pdf.cell(60, 10, student.fullname, 1)
        pdf.cell(15, 10, student.gender, 1)
        pdf.cell(80, 10, student.institution, 1)
        pdf.cell(20, 10, "{:,}".format(awarded_data.awarded), 1, ln=True)
        total +=awarded_data.awarded
        s_no += 1
        
    pdf.set_font("Arial", style='B', size=10)
    
    pdf.cell(9, 10, "", 1, 0, 'C', 1)
    pdf.cell(60, 10, "TOTAL", 1, 0, 'L', 1)
    pdf.cell(15, 10, "", 1, 0, 'L', 1)
    pdf.cell(80, 10, "", 1, 0, 'C', 1)
    pdf.cell(20, 10, "{:,}".format(total), 1, 0, 'L', 1)
    pdf.set_font("Arial", size=12)


    # #########################SEC ##########################
     #######sec_data
    all_disbursed_sec = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Secondary').values_list('user_id', flat=True)
    disbursed_users_personal_details_sec = PersonalDetails.objects.filter(user_id__in=all_disbursed_sec)
    disbursed_users_awarded_sec = UploadedDocuments.objects.filter(user_id__in=all_disbursed_sec)
   
    pdf.ln(20)

     # Create a table header
    pdf.set_fill_color(0, 191, 255)  # Light Blue
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0,6, f"[ii] Secondary Education", ln=True, align="L")
    pdf.set_font("Arial", style='B', size=8)


    pdf.cell(9, 10, "S/No.", 1, 0, 'L', 1)
    pdf.cell(60, 10, "Name", 1, 0, 'L', 1)
    pdf.cell(15, 10, "Gender", 1, 0, 'L', 1)
    pdf.cell(80, 10, "Institution", 1, 0, 'L', 1)
    pdf.cell(20, 10, "Amount", 1, 1, 'L', 1)

    # Create a table with student details
    pdf.set_fill_color(255, 255, 255)  # White
    pdf.set_font("Arial", size=8)
    s_no = 1
    total = 0
    for student, awarded_data in zip(disbursed_users_personal_details_sec, disbursed_users_awarded_sec):
        pdf.cell(9, 10, str(s_no), 1)
        pdf.cell(60, 10, student.fullname, 1)
        pdf.cell(15, 10, student.gender, 1)
        pdf.cell(80, 10, student.institution, 1)
        pdf.cell(20, 10, "{:,}".format(awarded_data.awarded), 1, ln=True)
        total +=awarded_data.awarded
        s_no += 1
        
    pdf.set_font("Arial", style='B', size=10)
    
    pdf.cell(9, 10, "", 1, 0, 'C', 1)
    pdf.cell(60, 10, "TOTAL", 1, 0, 'L', 1)
    pdf.cell(15, 10, "", 1, 0, 'L', 1)
    pdf.cell(80, 10, "", 1, 0, 'C', 1)
    pdf.cell(20, 10, "{:,}".format(total), 1, 0, 'L', 1)
    pdf.set_font("Arial", size=12)

    ####institution
    ###inst data
    try:
        awarded_id_list = User.objects.filter(last_name='Institution').values_list('id', flat=True)
        awarded = UploadedDocuments.objects.filter(application=last_application, user_id__in=awarded_id_list)
        
        # Check if there are no awarded records
        
    except UploadedDocuments.DoesNotExist:
        awarded = 'No Schools/Institution Has been Awarded yet.'

   
    pdf.ln(20)
    pdf.set_fill_color(0, 191, 255)  # Light Blue
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0,6, f"[iii] Institutions", ln=True, align="L")
    pdf.set_font("Arial", style='B', size=8)

    pdf.cell(9, 10, "S/No.", 1, 0, 'L', 1)
    pdf.cell(60+95, 10, "Institution Name", 1, 0, 'L', 1)
    pdf.cell(20, 10, "Amount", 1, 1, 'L', 1)

    s_no = 1
    total = 0
    for awards in awarded:
        pdf.cell(9, 10, str(s_no), 1)
        pdf.cell(60+95, 10, awards.user.first_name, 1)
        pdf.cell(20, 10, "{:,}".format(awards.awarded), 1, ln=True)
        total += awards.awarded
        s_no += 1
    
    pdf.set_font("Arial", style='B', size=10)
    
    pdf.cell(9, 10, "", 1, 0, 'C', 1)
    pdf.cell(60+95, 10, "TOTAL", 1, 0, 'L', 1)
    pdf.cell(20, 10, "{:,}".format(total), 1, 0, 'L', 1)
 
    pdf.ln(20)
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0,6, "Total Amount Disbursed = {:,}".format(approved_sum), ln=True, align="L")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Report-{owner.county}-{last_application}.pdf"'
    response.write(pdf.output(dest='S').encode('latin1'))
    return response



@staff_member_required
def forwarding_letter(request):
    current_application = Application.objects.last()

    # Get the user IDs of approved users in the current application
    approved_user_ids = UploadedDocuments.objects.filter(application_status='Approved', application=current_application).values_list('user_id', flat=True)

    # Get the PersonalDetails objects for approved users
    approved_users_personal_details = PersonalDetails.objects.filter(user_id__in=approved_user_ids)

    # Create a dictionary to store the grouped users by institution
    grouped_users_by_institution = {}

    # Group the approved users by their institution
    sorted_users = sorted(approved_users_personal_details, key=lambda x: x.institution)
    
    for institution, users in groupby(sorted_users, key=lambda x: x.institution):
        # Convert the 'users' iterator to a list to store all users for the institution
        grouped_users_by_institution[institution] = list(users)

    # Now, 'grouped_users_by_institution' contains a dictionary where keys are institutions, and values are lists of users for each institution.

    context = {
        'owner': OwnerDetails.objects.last(),
        'grouped_users_by_institution': grouped_users_by_institution
    }
    return render(request, 'users/forwarding_letter.html', context)




@staff_member_required
def reports(request):
    if request.method == 'POST':
        id = request.POST['id']
        print(f"Printing Id :   {id}")
        last_application = Application.objects.get(id_for_reference=id)
       
        owner = OwnerDetails.objects.last()

        approved_sum = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application).aggregate(Sum('awarded'))['awarded__sum'] or 0

        # all_approved = UploadedDocuments.objects.filter(application_status='Approved', application=last_application).values_list('user_id', flat=True)
        all_disbursed_higher = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Higher_Education').values_list('user_id', flat=True)

        # approved_users_personal_details = PersonalDetails.objects.filter(user_id__in=all_approved)
        disbursed_users_personal_details = PersonalDetails.objects.filter(user_id__in=all_disbursed_higher)

        # approved_users_awarded = UploadedDocuments.objects.filter(user_id__in=all_approved)
        disbursed_users_awarded = UploadedDocuments.objects.filter(user_id__in=all_disbursed_higher)
        # Count the number of records with application_status set to 'Disbursed'
        disbursed_count = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application).count() or 0

        disbursed_sec = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for = 'Secondary').count() or 0
        disbursed_high = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for="Higher_Education").count() or 0

        # Now, disbursed_count contains the count of 'Disbursed' records


    
        pdf = FPDF()

        pdf.add_page()

        pdf.set_font("Times", 'B', size=10)

            # Specify the image path and original width
        image_path = 'static/images/overall.jpg'
        original_img_width = 50  # Adjust this to the original width of your image

        # Calculate the new width for the image (e.g., half of the original width)
        img_width = original_img_width / 2

        # Set the x-coordinate to push the image to the left side (e.g., x=10 for a 10-unit margin)
        pdf.image(image_path, x=10, y=pdf.get_y(), w=img_width)


        # pdf.cell(0, 8, f"Date: {current_date}", ln=True, align="R")
        pdf.cell(0, 4, f"NG Constituency Development Fund Committee", ln=True, align="R")
        pdf.cell(0, 4, f"{owner.name}", ln=True, align="R")
        pdf.cell(0, 4, f"{owner.location}", ln=True, align="R")
        pdf.multi_cell(0, 4, f"{owner.p_o_box}, {owner.p_o_box_location}", align="R")
        pdf.multi_cell(0, 4, f"Tel: {owner.phone_number}", align="R")
        pdf.multi_cell(0, 4, f"Email:{owner.generation_email} / {owner.manager_email}", align="R")
        pdf.ln(4)
        pdf.cell(0, 4, f"{owner.county}",ln=True, align="L")
        pdf.ln(4)
    
        pdf.set_line_width(2)

        # Define the starting X and Y coordinates for the line
        x1 = 10  # 20px from the left margin
        x2 = pdf.w - 10  # 20px from the right margin
        y = pdf.get_y()  # Maintain the current Y position

        # Draw a horizontal line by drawing a line
        pdf.line(x1, y, x2, y)
        pdf.set_line_width(0.5)
        pdf.ln(4)
        pdf.set_font("Arial", style='B', size=16)

        pdf.cell(0,6, f"Report of {last_application.name_of_application}", ln=True, align="C")
        pdf.ln(4)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 5, f"Education plays a pivotal role in the development of individuals and communities, serving as a catalyst for progress and empowerment. In line with this belief, the Constituency Development Fund (CDF) - {owner.name} for the year {last_application.id_for_reference} embarked on a mission to transform lives through the provision of bursaries to deserving students within our constituency. This report serves as a comprehensive account of our commitment to enhancing educational opportunities and fostering a brighter future for our youth.")
        pdf.ln(4)
        pdf.multi_cell(0,5, 'The year {fy} marked a significant milestone as the CDF allocated substantial resources, amounting to Kshs. {t:,} to support the education of students in our constituency. These bursaries aimed not only to alleviate the financial burdens of students and their families but also to empower them to pursue higher education or secondary education and achieve their dreams.'.format(fy=last_application.id_for_reference,t=last_application.funds_available_for_secondary_schools + last_application.funds_available_for_universities))
        pdf.ln(4)
        pdf.multi_cell(0,5,"This report stands as a testament to the power of education, the unwavering support of the CDF, and the resilience of our students. It is a reflection of our collective commitment to nurturing talent, fostering academic achievement, and building a brighter future for our constituency.")

        pdf.ln(4)

        # Create a table header
        pdf.set_fill_color(0, 191, 255)  # Light Blue
        pdf.set_font("Arial",  size=10)
        pdf.cell(0,6, "Overview", ln=True, align="L")
        pdf.ln(3)

        pdf.cell(115, 10, "Item", 1, 0, 'L', 1)
        pdf.cell(60, 10, "Details", 1, 1, 'L', 1)
        

        pdf.cell(115, 10, "Financial Year", 1)
        pdf.cell(60, 10, f"{last_application.id_for_reference}", 1,ln=True)

        pdf.cell(115, 10, "Commencement Date", 1)
        pdf.cell(60, 10, f"{last_application.start_date}", 1,ln=True)

        pdf.cell(115, 10, "Conclusion Date", 1)
        pdf.cell(60, 10, f"{last_application.end_date}", 1,ln=True)

    ##################Applicants####
        pdf.cell(115, 10, "Total Number of Applicants", 1)
        pdf.cell(60, 10, f"{last_application.number_of_applicant}", 1,ln=True)

        pdf.cell(115, 10, "Number of Applicants Approved", 1)
        pdf.cell(60, 10, f"{disbursed_count}", 1,ln=True)


    #############Approved sec
        pdf.cell(115, 10, "Number of Applicants Benefited in Secondary", 1)
        pdf.cell(60, 10, f"{disbursed_sec}", 1,ln=True)
    #############Approved shigh

        pdf.cell(115, 10, "Number of Applicants Benefited in Higher Education", 1)
        pdf.cell(60, 10, f"{disbursed_high}", 1,ln=True)


        pdf.cell(115, 10, "Funds Allocated for Secondary Schools", 1)
        pdf.cell(60, 10, "Kshs. {:,}".format(last_application.funds_available_for_secondary_schools), 1,ln=True)


        pdf.cell(115, 10, "Funds Allocated for Higher Education", 1)
        pdf.cell(60, 10, "Kshs. {:,}".format(last_application.funds_available_for_universities), 1,ln=True)


    ##################distributed
        dis_sec = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Secondary').aggregate(Sum('awarded'))['awarded__sum'] or 0
        dis_higher = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Higher_Education').aggregate(Sum('awarded'))['awarded__sum'] or 0

        pdf.cell(115, 10, "Funds Disbursed to Secondary Schools", 1)
        pdf.cell(60, 10, "Kshs. {:,}".format(dis_sec), 1,ln=True)


        pdf.cell(115, 10, "Funds Disbursed for Higher Education", 1)
        pdf.cell(60, 10, f"Kshs. {dis_higher:,}", 1,ln=True)


    ##################remaining
        remain_sec = last_application.funds_available_for_secondary_schools - dis_sec
        remain_higher = last_application.funds_available_for_universities - dis_higher
        pdf.cell(115, 10, "Remaining Funds for Secondary Schools", 1)
        pdf.cell(60, 10, "Kshs. {:,}".format(remain_sec), 1,ln=True)


        pdf.cell(115, 10, "Remaining Funds for Higher Education", 1)
        pdf.cell(60, 10, "Kshs. {:,}".format(remain_higher), 1,ln=True)



        pdf.set_font("Arial", style='B', size=12)
        pdf.ln(14)

        pdf.cell(0,6, "[i] Higher Education", ln=True, align="L")
        pdf.set_font("Arial", style='B', size=8)


        pdf.cell(9, 10, "S/No.", 1, 0, 'L', 1)
        pdf.cell(60, 10, "Name", 1, 0, 'L', 1)
        pdf.cell(15, 10, "Gender", 1, 0, 'L', 1)
        pdf.cell(80, 10, "Institution", 1, 0, 'L', 1)
        pdf.cell(20, 10, "Amount", 1, 1, 'L', 1)

        # Create a table with student details
        pdf.set_fill_color(255, 255, 255)  # White
        pdf.set_font("Arial", size=8)
        s_no = 1
        total = 0
        for student, awarded_data in zip(disbursed_users_personal_details, disbursed_users_awarded):
            pdf.cell(9, 10, str(s_no), 1)
            pdf.cell(60, 10, student.fullname, 1)
            pdf.cell(15, 10, student.gender, 1)
            pdf.cell(80, 10, student.institution, 1)
            pdf.cell(20, 10, "{:,}".format(awarded_data.awarded), 1, ln=True)
            total +=awarded_data.awarded
            s_no += 1
            
        pdf.set_font("Arial", style='B', size=10)
        
        pdf.cell(9, 10, "", 1, 0, 'C', 1)
        pdf.cell(60, 10, "TOTAL", 1, 0, 'L', 1)
        pdf.cell(15, 10, "", 1, 0, 'L', 1)
        pdf.cell(80, 10, "", 1, 0, 'C', 1)
        pdf.cell(20, 10, "{:,}".format(total), 1, 0, 'L', 1)
        pdf.set_font("Arial", size=12)


        # #########################SEC ##########################
        #######sec_data
        all_disbursed_sec = UploadedDocuments.objects.filter(application_status='Disbursed', application=last_application,funds_for='Secondary').values_list('user_id', flat=True)
        disbursed_users_personal_details_sec = PersonalDetails.objects.filter(user_id__in=all_disbursed_sec)
        disbursed_users_awarded_sec = UploadedDocuments.objects.filter(user_id__in=all_disbursed_sec)
    
        pdf.ln(20)

        # Create a table header
        pdf.set_fill_color(0, 191, 255)  # Light Blue
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0,6, f"[ii] Secondary Education", ln=True, align="L")
        pdf.set_font("Arial", style='B', size=8)


        pdf.cell(9, 10, "S/No.", 1, 0, 'L', 1)
        pdf.cell(60, 10, "Name", 1, 0, 'L', 1)
        pdf.cell(15, 10, "Gender", 1, 0, 'L', 1)
        pdf.cell(80, 10, "Institution", 1, 0, 'L', 1)
        pdf.cell(20, 10, "Amount", 1, 1, 'L', 1)

        # Create a table with student details
        pdf.set_fill_color(255, 255, 255)  # White
        pdf.set_font("Arial", size=8)
        s_no = 1
        total = 0
        for student, awarded_data in zip(disbursed_users_personal_details_sec, disbursed_users_awarded_sec):
            pdf.cell(9, 10, str(s_no), 1)
            pdf.cell(60, 10, student.fullname, 1)
            pdf.cell(15, 10, student.gender, 1)
            pdf.cell(80, 10, student.institution, 1)
            pdf.cell(20, 10, "{:,}".format(awarded_data.awarded), 1, ln=True)
            total +=awarded_data.awarded
            s_no += 1
            
        pdf.set_font("Arial", style='B', size=10)
        
        pdf.cell(9, 10, "", 1, 0, 'C', 1)
        pdf.cell(60, 10, "TOTAL", 1, 0, 'L', 1)
        pdf.cell(15, 10, "", 1, 0, 'L', 1)
        pdf.cell(80, 10, "", 1, 0, 'C', 1)
        pdf.cell(20, 10, "{:,}".format(total), 1, 0, 'L', 1)
        pdf.set_font("Arial", size=12)

        ####institution
        ###inst data
        try:
            awarded_id_list = User.objects.filter(last_name='Institution').values_list('id', flat=True)
            awarded = UploadedDocuments.objects.filter(application=last_application, user_id__in=awarded_id_list)
            
            # Check if there are no awarded records
            
        except UploadedDocuments.DoesNotExist:
            awarded = 'No Schools/Institution Has been Awarded yet.'

    
        pdf.ln(20)
        pdf.set_fill_color(0, 191, 255)  # Light Blue
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0,6, f"[iii] Institutions", ln=True, align="L")
        pdf.set_font("Arial", style='B', size=8)

        pdf.cell(9, 10, "S/No.", 1, 0, 'L', 1)
        pdf.cell(60+95, 10, "Institution Name", 1, 0, 'L', 1)
        pdf.cell(20, 10, "Amount", 1, 1, 'L', 1)

        s_no = 1
        total = 0
        for awards in awarded:
            pdf.cell(9, 10, str(s_no), 1)
            pdf.cell(60+95, 10, awards.user.first_name, 1)
            pdf.cell(20, 10, "{:,}".format(awards.awarded), 1, ln=True)
            total += awards.awarded
            s_no += 1
        
        pdf.set_font("Arial", style='B', size=10)
        
        pdf.cell(9, 10, "", 1, 0, 'C', 1)
        pdf.cell(60+95, 10, "TOTAL", 1, 0, 'L', 1)
        pdf.cell(20, 10, "{:,}".format(total), 1, 0, 'L', 1)
    
        pdf.ln(20)
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(0,6, "Total Amount Disbursed = {:,}".format(approved_sum), ln=True, align="L")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Report-{owner.county}-{last_application}.pdf"'
        response.write(pdf.output(dest='S').encode('latin1'))
        return response
    try:
        all_application = Application.objects.all()

    except Application.DoesNotExist:
        all_application = "No Active Application."

    context = {
        'owner':OwnerDetails.objects.last(),
        'last_application':Application.objects.last(),
        'all_applications':all_application,
    }
    return render(request, 'users/reports.html',context)

@staff_member_required
def forwarding_letter_institution(request, institution):
    current_application = Application.objects.last()
    owner = OwnerDetails.objects.last()

    # Get the user IDs of approved users in the current application
    approved_user_ids = UploadedDocuments.objects.filter(application_status='Approved', application=current_application).values_list('user_id', flat=True)
    approved_users_personal_details = PersonalDetails.objects.filter(user_id__in=approved_user_ids,institution=institution)
    approved_users_personal_details_id = PersonalDetails.objects.filter(user_id__in=approved_user_ids,institution=institution).values_list('user_id', flat=True)

    personal_details = PersonalDetails.objects.filter(user_id__in=approved_user_ids,institution=institution).last()
    uploaded_users_data = UploadedDocuments.objects.filter(user_id__in=approved_users_personal_details_id,application=current_application)
    
        # Assuming you have already filtered the queryset to include relevant documents
    awarded_sum = UploadedDocuments.objects.filter(
        user_id__in=approved_users_personal_details_id,  # Filter by user IDs
        application=current_application,  # Filter by application
    ).aggregate(total_awarded=Sum('awarded'))

    # The 'total_awarded' key in the result dictionary contains the sum of 'awarded' values
    total_awarded_value = awarded_sum.get('total_awarded', 0)  # Get the value or default to 0 if None
    total_awarded_in_words = num2words(total_awarded_value)
    total_awarded_in_words = total_awarded_in_words.title()

    Email_Address = request.user.email
    Constituency_Name = owner.name
    fullname=request.user.first_name + ' '+ request.user.last_name
    
    current_date_formatted = date(datetime.now(), "F d, Y")
    # print(f"Date: {current_date_formatted}")



    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Times", 'B', size=10)

        # Specify the image path and original width
    image_path = 'static/images/overall.jpg'
    original_img_width = 50  # Adjust this to the original width of your image

    # Calculate the new width for the image (e.g., half of the original width)
    img_width = original_img_width / 2

    # Set the x-coordinate to push the image to the left side (e.g., x=10 for a 10-unit margin)
    pdf.image(image_path, x=10, y=pdf.get_y(), w=img_width)


    # pdf.cell(0, 8, f"Date: {current_date}", ln=True, align="R")
    pdf.cell(0, 4, f"NG Constituency Development Fund Committee", ln=True, align="R")
    pdf.cell(0, 4, f"{Constituency_Name}", ln=True, align="R")
    pdf.cell(0, 4, f"{owner.location}", ln=True, align="R")
    pdf.multi_cell(0, 4, f"{owner.p_o_box}, {owner.p_o_box_location}", align="R")
    pdf.multi_cell(0, 4, f"Tel: {owner.phone_number}", align="R")
    pdf.multi_cell(0, 4, f"Email:{owner.generation_email} / {owner.manager_email}", align="R")
    pdf.ln(4)
    pdf.cell(0, 4, f"{owner.county}",ln=True, align="L")
    pdf.ln(4)
   
    pdf.set_line_width(2)

    # Define the starting X and Y coordinates for the line
    x1 = 10  # 20px from the left margin
    x2 = pdf.w - 10  # 20px from the right margin
    y = pdf.get_y()  # Maintain the current Y position

    # Draw a horizontal line by drawing a line
    pdf.line(x1, y, x2, y)
    pdf.set_line_width(0.5)
    pdf.ln(4)

    pdf.cell(0, 4, f"REF:..................................................................................................", align="L")
    pdf.cell(0, 4, f"{current_date_formatted}", ln=True, align="R")


    pdf.ln(6)
    pdf.cell(0, 5.5, f"The Finance Department,", ln=True, align="L")
    pdf.cell(0, 5.5, f"{institution},", ln=True, align="L")
    pdf.cell(0, 5.5, f"P. O. Box: {personal_details.institution_postal_address},", ln=True, align="L")

    
    pdf.ln(5)
    pdf.set_font("Times", 'B', size=12)

    pdf.cell(0,6, "Dear Sir/Madam,", ln=True, align="L")
    pdf.ln(3)


    pdf.multi_cell(0, 6, f"RE: Bursary Allocation For FY {current_application.id_for_reference}.")
    pdf.set_line_width(.5)

    # Define the starting X and Y coordinates for the line
    x1 = 11  # 20px from the left margin
    x2 = pdf.w - 120 # 20px from the right margin
    y = pdf.get_y()  # Maintain the current Y position

    # Draw a horizontal line by drawing a line
    pdf.line(x1, y, x2, y)
    pdf.set_line_width(0.5)

    pdf.ln(3)
    pdf.set_font("Times", size=12)
    # total_awarded_value = "{:,}".format(total_awarded_value)
    # pdf.multi_cell(0,6,f'Enclosed herewith, please find Cheque no:........................... amounting to Kshs. {total_awarded_in_words} ({total_awarded_value}/=) only dated {current_date_formatted} in the benefit of the students listed below:-')
    pdf.multi_cell(0,6,'Enclosed herewith, please find Cheque no:........................... amounting to Kshs. {a} ({t:,}/=) only dated {c} in the benefit of the students listed below:-'.format(a=total_awarded_in_words, c=current_date_formatted,t=total_awarded_value))
    pdf.ln(3)

    # Create a table header
    pdf.set_fill_color(0, 191, 255)  # Light Blue
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0,6, f"{institution}", ln=True, align="C")
    pdf.set_font("Arial", style='B', size=8)


    pdf.cell(9, 10, "S/No.", 1, 0, 'L', 1)
    pdf.cell(60, 10, "Name", 1, 0, 'L', 1)
    pdf.cell(60, 10, "Course", 1, 0, 'L', 1)
    pdf.cell(35, 10, "Admission Number", 1, 0, 'L', 1)
    pdf.cell(20, 10, "Amount", 1, 1, 'L', 1)

    # Create a table with student details
    pdf.set_fill_color(255, 255, 255)  # White
    pdf.set_font("Arial", size=8)
    s_no = 1
    for student, awarded_data in zip(approved_users_personal_details, uploaded_users_data):
        pdf.cell(9, 10, str(s_no), 1)
        pdf.cell(60, 10, student.fullname, 1)
        pdf.cell(60, 10, student.course, 1)
        pdf.cell(35, 10, student.admin_no, 1)
        pdf.cell(20, 10, "{:,}".format(awarded_data.awarded), 1, ln=True)
        UploadedDocuments.objects.filter(user=student.user,application=current_application).update(application_status = 'Disbursed')
        s_no += 1
        
    pdf.set_font("Arial", style='B', size=10)
    
    pdf.cell(9, 10, "", 1, 0, 'C', 1)
    pdf.cell(60, 10, "TOTAL", 1, 0, 'L', 1)
    pdf.cell(60, 10, "", 1, 0, 'L', 1)
    pdf.cell(35, 10, "", 1, 0, 'C', 1)
    pdf.cell(20, 10, "{:,}".format(total_awarded_value), 1, 1, 'L', 1)
    pdf.set_font("Arial", size=12)

    pdf.ln(10)
    pdf.multi_cell(0,8,'Please acknowledge formally receipt of the above cheque and in case of any changes the CDF office has all the discretion to award any needy students.')
    pdf.cell(0,6, "Thank you for your co-operation.")
    pdf.ln(20)
    pdf.cell(0,6,"Yours's Faithfully,")
    pdf.ln(20)
    pdf.cell(0,6,f"{owner.name_of_the_chairperson},", ln=True)
   
    pdf.cell(0,6,"CDF Chairperson.", ln=True)

    pdf.cell(0,6,f"{owner.name}.", ln=True)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Bursary_Award_Letter-{institution}_FY_{current_application.id_for_reference}.pdf"'
    response.write(pdf.output(dest='S').encode('latin1'))
    return response






@staff_member_required
def create_institution(request):
    if request.method == 'POST':
        institution_name = request.POST["institution_name"]
        institution_Reference = request.POST['institution_Reference']

        if User.objects.filter(username=institution_Reference):
            messages.error(request, f"Institution with {institution_Reference} already exists. Try again!")
            return redirect('create_institution')
        new_inst = User.objects.create_user(institution_Reference)
        new_inst.first_name  = institution_name
        new_inst.last_name  = 'Institution'
        new_inst.save()
        messages.success(request, "Institution has been successfully created.")
        return redirect('create_institution')
    


    try:
        current_application = Application.objects.last()

    except:
        current_application = 'No Active Application.'

    try:
        awarded_id_list = User.objects.filter(last_name='Institution').values_list('id', flat=True)
        awarded = UploadedDocuments.objects.filter(application=current_application, user_id__in=awarded_id_list)
        
        # Check if there are no awarded records
        
    except UploadedDocuments.DoesNotExist:
        awarded = 'No Schools/Institution Has been Awarded yet.'


    context = {
        'owner':OwnerDetails.objects.last(),
        'institutions':User.objects.filter(last_name='Institution'),
        'application':current_application,
        'awarded':awarded,
    }
    return render(request, 'users/create_institution.html',context)



@staff_member_required#
def institution_profile(request, inst_name):
    institution = get_object_or_404(User, username=inst_name)

    try:
        current_application = Application.objects.last()

    except:
        current_application = 'Application is Created Yet.'
    
    if request.method == 'POST':
        amount = request.POST["amount"]
        if UploadedDocuments.objects.filter(application=current_application,user=institution):
            messages.error(request, f"The {institution.first_name} already Awarded.")
            return redirect('create_institution')
        else:
            awarding = UploadedDocuments(
                user=institution,
                awarded= amount,
                funds_for = 'Secondary',
                application_status = 'Disbursed',
                application=current_application,
                approved_by=request.user.first_name + " "+ request.user.last_name,
            )
            awarding.save()
            messages.info(request, f"The {institution.first_name} has been Awarded {amount}.")
            return redirect('create_institution')




    context = {
       'institution':institution,
       'owner':OwnerDetails.objects.last() 
    }
    return render(request, "users/inst_award.html",context)









