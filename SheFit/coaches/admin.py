from django.contrib import admin
from .models import Coach,CoachComment

# Register your models here.
class CoachCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "coach", "type", "rating")
    list_filter = ("coach", "rating")


class CoachAdmin(admin.ModelAdmin):
    list_display = ("user", "gym")
    list_filter = ("gym",)


admin.site.register(Coach, CoachAdmin)
admin.site.register(CoachComment, CoachCommentAdmin)