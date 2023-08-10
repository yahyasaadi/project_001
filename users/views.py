from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
# from django.conf import settings
from CDF import settings
# from django.http import HttpResponse
from .tokens import generate_token
from .models import OwnerDetails

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
            return render(request, "users/home.html",{"fname":fname})
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('signin')
    owner = OwnerDetails.objects.first()  
    return render(request, "users/signin.html",{'owner':owner})


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')
