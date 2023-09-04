from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('signin', views.signin, name="signin"),
    path('staff_dashboard', views.staff_dashboard, name="staff_dashboard"),
    path('signout', views.signout, name="signout"),
    path('personal_details', views.personal_details, name="personal_details"),
    path('update_personal_details', views.update_personal_details, name="update_personal_details"),
    path('family_background', views.family_background, name="family_background"),
    path('update_family_background', views.update_family_background, name="update_family_background"),
    path('additional_info', views.additional_info, name="additional_info"),
    path('update_additional_info', views.update_additional_info, name="update_additional_info"),
    path('academic_performance', views.academic_performance, name="academic_performance"),
    path('update_academic_performance', views.update_academic_performance, name="update_academic_performance"),
    path('approved_lst_pdf', views.approved_lst_pdf, name="approved_lst_pdf"),
    path('download', views.generate_pdf, name="download"),
    path('apply', views.apply, name="apply"),
    path('new_application', views.new_application, name="new_application"),
    path('forwarding_letter', views.forwarding_letter, name="forwarding_letter"),
    path('institutions', views.create_institution, name="create_institution"),
    
    path('update_current_application', views.update_current_application, name="update_current_application"),
    path("generate_bursary_letter/<int:user_id>", views.generate_bursary_letter, name="generate_bursary_letter"),
    

    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('institution/<str:inst_name>/', views.institution_profile, name='institution_profile'),
    path('forwarding_letter_institution/<str:institution>/', views.forwarding_letter_institution, name='forwarding_letter_institution'),

    path('students_dashboard/', views.studentsDashboard, name="students_dashboard"),
    path('list_of_applicants/', views.list_of_applicants, name="list_of_applicants"),
    path('orphans_or_disability/', views.orphans_or_disability, name="orphans_or_disability"),
    path('returning_applicants/', views.returning_applicants, name="returning_applicants"),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)