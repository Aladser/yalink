from django.contrib import admin
from authen.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_active', 'auth_type')
    search_fields = ('first_name', 'last_name')
