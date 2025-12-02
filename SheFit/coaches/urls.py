from django.urls import path

from . import views


app_name = "coaches"

urlpatterns=[
 path('all/',views.all_coaches_view,name="all_coaches_view"),
 path('profile/<int:coach_id>/',views.profile_coach_view,name="profile_coach_view"),
path('comment/add/<coach_id>/',views.add_comment_view ,name="add_comment_view"),
]