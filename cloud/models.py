from django.db import models
import datetime
import os
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.middleware import SessionMiddleware

class CustomUser(AbstractUser):
    pass
    available_space = models.FloatField(default=100)
    used_space = models.FloatField(default=0)
    creation_date = models.DateField(auto_now_add=True)
    directory = models.CharField(max_length=100,default='')

    def __str__(self):
        return f"{self.username},{self.creation_date} {self.available_space} {self.used_space}"

    def update_used_space(self, file_size):
        if self.used_space + file_size < self.available_space:
            self.used_space =  self.used_space + file_size
            self.save()
            return True
        else:
            return False

    def get_full_available_space(self):
        return self.available_space - self.used_space

    def get_available_space(self):
        return round((self.available_space - self.used_space)/(1024*1024) ,2)

    def get_used_percent(self):
        return round((self.used_space/self.available_space)*100,2)


class Folder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    is_root = models.BooleanField(default=False)
    path = models.CharField(max_length=100)
    superior_path = models.CharField(max_length=100)

    def __str__(self):
        return self.name

def get_upload_path(instance, filename):
    return os.path.join(instance.user.username, filename)

class File(models.Model):
    name = models.CharField(max_length=40)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    size = models.FloatField(default=0)
    file = models.FileField(upload_to=get_upload_path,default='')
    is_shared = models.BooleanField(default=False)
    share_link = models.CharField(max_length=140, default="")

    def __str__(self):
        return f"{self.name}, size:{self.size}B"

class Context(models.Model):
    main_text_index = models.CharField(max_length = 40, default="FRIENDLY USER CLOUD")
    subtitle_index = models.CharField(max_length = 150, default="Przechowamy Twoje pliki :)")
    footer = models.CharField(max_length=150, default="CREATED BY KRZYSZTOF IŁENDO, MARCIN GRABOWIECKI AND ŁUKASZ HOSSA")
    login_link = models.CharField(max_length = 40, default="LOGIN")
    logout_link = models.CharField(max_length = 40, default="LOGOUT")
    register_link = models.CharField(max_length = 40, default="REGISTER")
    welcome_logged_user_link = models.CharField(max_length = 40, default="Welcome, ")
    welcome_user_files_view = models.CharField(max_length = 50, default="WITAJ")
    go_to_your_files_button = models.CharField(max_length = 40, default="Przejdź do swoich plików")
    subtitle_files_view = models.CharField(max_length = 50, default="Oto Twoje pliki")


    def __str__(self):
        return "Edytując ten obiekt możesz zmienić wartości wyświetlane na stronie"
