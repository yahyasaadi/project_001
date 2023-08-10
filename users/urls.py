from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('personal_details', views.personal_details, name="personal_details"),
    path('family_background', views.family_background, name="family_background"),
    
    path('students_dashboard/', views.studentsDashboard, name="students_dashboard"),
    
]