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
# from django.conf import settings
from CDF import settings
# from django.http import HttpResponse
from .tokens import generate_token
from .models import OwnerDetails, PersonalDetails, FamilyBackaground, Sibling, AdditionalInformation, AcademicPerformance, Application, UploadedDocuments
from fpdf import FPDF
from datetime import datetime


# Create your views here.
def home(request):
    owner = OwnerDetails.objects.first()
    return render(request, "users/home.html",{'owner':owner})

def signup(request):
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
        messages.success(request, "Your account has been successfully created.")


        # subject = "Welcome to Dadaab CDF Login!!"
        # message = "Hello " + new_user.first_name + "!! \n" + "Welcome to GFG!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nYahya Saadi"        
        # from_email = settings.EMAIL_HOST_USER
        # to_list = [new_user.email]
        # send_mail(subject, message, from_email, to_list, fail_silently=True)
        # send_mail("Welcome to Dadaab CDF Login!!", "The message", "yahyasaadi9219@gmail.com", ["yahyasnoor@gmail.com"], fail_silently=True)

        # welcome email
        email = EmailMessage(
            subject="Welcome to Dadaab CDF Login!!",
            body="Hello " + new_user.first_name + "!! \n" + "Welcome to Dadaab CDF. \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nYahya Saadi",
            from_email=settings.EMAIL_HOST_USER,
            to=[new_user.email],
        )
        email.fail_silently = True
        email.send()


        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Dadaab Login!"
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
    return render(request, "users/signup.html")



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
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')
    

@login_required
def studentsDashboard(request):
    fname = request.user.first_name
    owner = OwnerDetails.objects.first()  
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
            id_or_passport_no= id_or_passport_no,
            gender=gender,
            date_of_birth=date_of_birth,
            institution=institution,
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
            id_or_passport_no= id_or_passport_no,
            gender=gender,
            date_of_birth=date_of_birth,
            institution=institution,
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
            fname = user.first_name

            if user.is_staff:
                return redirect('staff_dashboard')
            # messages.success(request, "Logged In Sucessfully!!")
            return redirect('students_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('signin')
    owner = OwnerDetails.objects.first()  
    return render(request, "users/signin.html",{'owner':owner})


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')


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
    approved_sum = UploadedDocuments.objects.filter(application_status='Approved').aggregate(Sum('awarded'))['awarded__sum']
    approved_sum_secondary = UploadedDocuments.objects.filter(application_status='Approved',funds_for='Secondary').aggregate(Sum('awarded'))['awarded__sum']
    approved_sum_higher_education = UploadedDocuments.objects.filter(application_status='Approved', funds_for='Higher_Education').aggregate(Sum('awarded'))['awarded__sum']
    approved_user_ids = UploadedDocuments.objects.filter(application_status='Approved', application=application).values_list('user_id', flat=True)
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

    all_applied_user_ids = set(previous_and_current_applied_user_ids).intersection(set(current_applied_user_ids))
    
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


# @login_required
# def review(request):
#     owner = OwnerDetails.objects.first()
#     personal_details = PersonalDetails.objects.get(user = request.user)
#     family_background = FamilyBackaground.objects.get(user = request.user)
#     siblings = Sibling.objects.filter(user = request.user)
#     additional_info = AdditionalInformation.objects.get(user = request.user)
#     academic_performance = AcademicPerformance.objects.get(user = request.user)
#     context = {
#         'owner':owner,
#         'personal_details':personal_details,
#         'family_background':family_background,
#         'siblings':siblings,
#         'additional_info':additional_info,
#         'academic_performance':academic_performance
#         }
#     return render(request, 'users/review.html',context)



@login_required
def generate_pdf(request):
    owner = OwnerDetails.objects.first()
    personal_details = PersonalDetails.objects.get(user = request.user)
    family_background = FamilyBackaground.objects.get(user = request.user)
    siblings = Sibling.objects.filter(user = request.user)
    additional_info = AdditionalInformation.objects.get(user = request.user)
    academic_performance = AcademicPerformance.objects.get(user = request.user)



    response = HttpResponse(content_type='application/pdf')
    
    user_full_name = request.user.get_full_name()  # Get the user's full name
    current_date= datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Get the current date in YYYY-MM-DD format
    current_date1= datetime.now().strftime("%Y-%m-%d, Time: %H:%M:%S")  # Get the current date in YYYY-MM-DD format
    
    filename = f"{user_full_name}_{current_date}.pdf"  # Combine user's name and date
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    class PDF(FPDF):
        def header(self):
            self.set_font('Times', 'B', 8)
            self.cell(0, 10, f'CDF Application form for {owner.name}', 0, 1, 'R')
            self.cell(0, 5, f'Date: {current_date1}', 0, 1, 'L')
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Times', 'I', 8)
            self.cell(0, 10, 'Name of the Applicant: ' + request.user.get_full_name(), 0, 0, 'L')
            self.cell(0, 10, 'Produced By: CDF Office representing the ' + owner.name, 0, 0, 'R')

    pdf = PDF()
    pdf.add_page()
    

      # Add some vertical spacing
    
    # pdf.image('static/images/overall.jpg', x=10, y=pdf.get_y(), w=10)
    image_path = 'static/images/overall.jpg'
    original_img_width = 50  # Adjust this to the original width of your image
    img_width = original_img_width / 2  # Half of the original width
    pdf.image(image_path, x=pdf.w / 2 - img_width / 2, y=pdf.get_y(), w=img_width)
    pdf.ln(20)
    pdf.set_font("Times", 'B', 16)
    pdf.cell(0, 10, f"{owner.name} Bursary", ln=True, align='C')
    pdf.set_font("Times", 'B', 8)
    pdf.cell(0, 10, f"P.O. BOX 732-90200, {owner.name}. TEL: 0734-909- 303 & 0726242177. Email.cdfdadaab@ngcdf.go.ke", ln=True, align='C')
    
    pdf.ln(4)
    pdf.set_font("Times", 'B', 16)
    pdf.cell(0, 10, "PART A: INSTRUCTION", ln=True, align='L')
    
    content = (
    "1. The constituency bursary scheme has limited available funds and is meant to support only the very needy cases.\n"
    "    Persons who are able are not expected to apply.\n"
    "2. It is an offense to give false information and once discovered will lead to disqualification.\n"
    "3. Total and Partial orphans MUST present supporting documents from the area chief or Religious Leader.\n"
    "4. All forms shall be returned at the {0} NG-CDF offices not later than {t}.\n"
    "\t\t\t\tNB: Any form returned after the stipulated period shall not be accepted whatsoever.\n"
    "5. Successful applicants will have the awarded bursary paid directly to university or college.\n"
    "6. All information provided will be verified with the relevant Authority(s).\n"
    "7. Applicants must upload the completed form along with supporting documents to the CDF Portal."
    ).format(owner.name, t="7th April 2023")

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
    pdf.cell(0, 10, "ii. APPLICANT'S ADDITIONAL INFORMATION", ln=True, align='L')
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
    pdf.ln(34)

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


def apply(request):
    if request.method=='POST':
        user = request.user
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        id_card = request.FILES.get('id_card')
        transcript_report_form = request.FILES.get('transcript_report_form')
        parents_guardians_id_card = request.FILES.get('parents_guardians_id_card')
        students_id_card = request.FILES.get('students_id_card')
        birth_certificate = request.FILES.get('birth_certificate')
        parents_death_certificate = request.FILES.get('parents_death_certificate')
        fees_structure = request.FILES.get('fees_structure')
        admission_letters = request.FILES.get('admission_letters')
        verification_document = request.FILES.get('verification_document')
        uploaded_documents = UploadedDocuments(
            user=user,
            application=Application.objects.last(),
            id_card=id_card,
            transcript_report_form=transcript_report_form,
            parents_guardians_id_card=parents_guardians_id_card,
            students_id_card=students_id_card,
            birth_certificate=birth_certificate,
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
            owner = OwnerDetails.objects.first()
            return render(request, 'users/success.html',{'owner':owner})
        
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
            
        print(already)
        if last_application:
            # Get the current date
            current_date = datetime.now().date()

            # Compare the end_date with the current date
            if last_application.end_date > current_date and last_application.is_active :
                # The end_date has passed
                print("The end date has not passed.")
                if already is None:
                    owner = OwnerDetails.objects.first()
                    return render(request, 'users/uploading.html',{'owner':owner,'last_application':last_application})
                else:
                    return HttpResponse(f'You have already applied and your application status: {already.application_status}')

            else:
                # The end_date has not passed
                print("The end date has passed.")
                return HttpResponse(f'You passed the deadline which was {last_application.end_date}')
        else:
            # No Application instance exists
            print("No Application instance found.")
            return HttpResponse('No application found yet')