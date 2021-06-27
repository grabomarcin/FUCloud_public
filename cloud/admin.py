from django.contrib import admin
from .models import File, CustomUser, Folder, Context
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username','available_space', 'used_space']


admin.site.register(CustomUser, CustomUserAdmin)
#admin.site.register(Directory)
admin.site.register(File)
admin.site.register(Folder)
admin.site.register(Context)
