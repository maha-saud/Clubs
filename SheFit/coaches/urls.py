from django.urls import path

from . import views


app_name = "coaches"

urlpatterns=[
    path('all/',views.all_coaches_view,name="all_coaches_view"),
    path('profile/<int:coach_id>/',views.profile_coach_view,name="profile_coach_view"),
    path("update/<coach_id>/", views.coach_update_view, name="coach_update_view"),
    path("delete/<coach_id>/", views.coach_delete_view, name="coach_delete_view"),
    path('comment/add/<coach_id>/',views.add_comment_view ,name="add_comment_view"),
]