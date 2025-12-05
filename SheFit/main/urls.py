from django.urls import path

from . import views


app_name = "main"


urlpatterns=[
   path('',views.home_view,name="home_view"),
   path('mode/<mode>/',views.mode_view,name="mode_view"),
   path('search/',views.search_view,name="search_view"),
   path("about/", views.about_view, name="about_view"),

]