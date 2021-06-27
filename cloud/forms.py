from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, File, Folder
import os
from django.conf import settings
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your forms here.

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2",)
        exclude = ("available_space",)

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        dirname = user.username # 2010.08.09.12.08.45
        try:
            path = os.path.join(settings.MEDIA_ROOT, dirname)
            os.mkdir(path)
            folder = Folder(user = user, name = user.username, is_root = True, path = path)
            folder.save()
        except:
            print("Błąd dodawania folderu")
        return user



class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class FileForm(forms.ModelForm):
    class Meta:
        model = File

        fields = [
            'file'
        ]
        exclude = [
            'size', 'user', 'name','is_shared',
        ]

class FolderForm(forms.ModelForm):

    class Meta:
        model = Folder

        fields = [
            'name'
        ]
        exclude = [
            'user', 'is_root', 'path', 'superior_path',
        ]



