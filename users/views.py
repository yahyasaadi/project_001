from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required
# from django.conf import settings
from CDF import settings
# from django.http import HttpResponse
from .tokens import generate_token
from .models import OwnerDetails, PersonalDetails, FamilyBackaground, Sibling, AdditionalInformation, AcademicPerformance

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
        return HttpResponse('Saved')
    else:
        
        owner = OwnerDetails.objects.first() 
        return render(request, 'users/family_background.html',{"owner":owner})
    
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
        ward = request.POST['ward']
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
            ward=ward,
            institution_postal_address= institution_postal_address,
            institution_telephone_no=institution_telephone_no,
            ammount_requesting=ammount_requesting
        )
        saved = saving_personal_details.save()

        return redirect('fa')

    else:
        owner = OwnerDetails.objects.first() 
        return render(request, 'users/personal_details.html',{"owner":owner})

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name

            if user.is_staff:
                fname = user.first_name

                return render(request,'users/staff_page.html',{"fname":fname})
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
        return HttpResponse('Saved')
    else:
        owner = OwnerDetails.objects.first() 
        return render(request, 'users/additional_info.html',{"owner":owner})


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
        return HttpResponse('Saved')
    else:
        owner = OwnerDetails.objects.first() 
        return render(request, 'users/academic_performance.html',{"owner":owner})