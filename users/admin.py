from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'date_of_birth', 'google_id', 'profile_picture', 'created_at')
    list_filter = ('created_at', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'email', 'google_id') 
