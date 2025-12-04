from django.urls import path

from . import views


app_name = "accounts"

urlpatterns=[
   path('signin/',views.signin_view,name="signin_view"),
   path('signup/',views.signup_view,name="signup_view"),
   path('signup/coach',views.coach_signup_view,name="coach_signup_view"),
   path('signup/gym',views.gym_signup_view,name="gym_signup_view"),
   path('signup/trainee',views.trainee_signup_view,name="trainee_signup_view"),
   path('logout/',views.logout_view,name="logout_view"),
   path('profile/<int:train_id>/',views.profile_trainee_view,name="profile_trainee_view"),
]