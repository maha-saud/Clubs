from django.urls import path

from . import views


app_name = "coaches"

urlpatterns=[
    path('all/',views.all_coaches_view,name="all_coaches_view"),
    path('profile/<int:coach_id>/',views.profile_coach_view,name="profile_coach_view"),
    path('add/plan/', views.add_plan_view, name="add_plan_view"),
    path("update/plan/<plan_id>/", views.update_plan_view, name="update_plan_view"),
    path("delete/plan/<plan_id>/", views.delete_plan_view, name="delete_plan_view"),
    path('plans/<int:coach_id>/',views.plans_list_view,name="plans_list_view"),
    path("update/<coach_id>/", views.coach_update_view, name="coach_update_view"),
    path("delete/<coach_id>/", views.coach_delete_view, name="coach_delete_view"),
    path('comment/add/<coach_id>/',views.add_comment_view ,name="add_comment_view"),
]