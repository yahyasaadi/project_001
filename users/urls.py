from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('personal_details', views.personal_details, name="personal_details"),
    path('update_personal_details', views.update_personal_details, name="update_personal_details"),
    path('family_background', views.family_background, name="family_background"),
    path('update_family_background', views.update_family_background, name="update_family_background"),
    path('additional_info', views.additional_info, name="additional_info"),
    path('update_additional_info', views.update_additional_info, name="update_additional_info"),
    path('academic_performance', views.academic_performance, name="academic_performance"),
    path('update_academic_performance', views.update_academic_performance, name="update_academic_performance"),
    # path('review', views.review, name="review"),
    path('download', views.generate_pdf, name="download"),
    
    path('students_dashboard/', views.studentsDashboard, name="students_dashboard"),
    
]