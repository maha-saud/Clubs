from django.urls import path
from . import views

app_name = "gyms"

urlpatterns=[
    path("detail/<gym_id>/", views.gym_detail_view, name="gym_detail_view"),
    path("update/<gym_id>/", views.gym_update_view, name="gym_update_view"),
    path("delete/<gym_id>/", views.gym_delete_view, name="gym_delete_view"),
    path("<hood_name>/", views.all_gyms_view, name="all_gyms_view"),
    path("comment/add/<gym_id>/", views.add_comment_view, name="add_comment_view"),
    path("comments/reply/<comment_id>/", views.add_reply_view, name="add_reply_view"),
    path('toggle_coach/<int:gym_id>/', views.toggle_coach_gym, name="toggle_coach_gym"),
    path("comment/delete/<int:comment_id>/", views.delete_comment_view, name="delete_comment_view"),




]