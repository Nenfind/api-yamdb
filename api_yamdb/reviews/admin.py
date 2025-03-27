from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    model = User
    fieldset = ['bio', 'role', 'username', 'email', 'first_name', 'last_name']

admin.site.register(User, UserAdmin)
