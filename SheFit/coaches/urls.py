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
    path('plans/<plan_id>/checkout',views.checkout_srtipe_view ,name="checkout_srtipe_view"),
    path('payment/success',views.payment_success ,name="payment_success"),
    path('payment/cancel',views.payment_cancel ,name="payment_cancel"),
    path("cart/",views.cart_view,name="cart_view"),
    path("cart/add/<int:plan_id>",views.add_to_cart_view,name="add_to_cart_view"),
    path("cart/remove/",views.remove_from_cart_view,name="remove_from_cart_view"),
    path('add/post/', views.add_post_view, name="add_post_view"),
    path("update/post/<post_id>/", views.update_post_view, name="update_post_view"),
    path("delete/post/<post_id>/", views.delete_post_view, name="delete_post_view"),
]