from django.contrib import admin

# Register your models here.
from User.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'country')
    list_filter = ('user',)


admin.site.register(Profile, ProfileAdmin)
