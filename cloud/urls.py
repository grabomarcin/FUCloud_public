from django.urls import path

from . import views
app_name = 'cloud'
urlpatterns = [
    path('', views.index, name='index'),
    path('files', views.files, name='files'),
    path('back_to_superior', views.back_to_superior, name='back_to_superior'),
    path('files/add_folder', views.add_folder, name='add_folder'),
    path('files/<folder_name>', views.go_to_folder, name='go_to_folder'),
    path('delete/<file>', views.delete_file, name='delete_file'),
    path('delete_folder/<folder>', views.delete_folder, name='delete_folder'),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path('upload', views.upload, name="upload"),
    path('share_file/<file>', views.share_file, name="share_file"),
    path('share/<file>', views.share, name="share"),
    path('stop_sharing/<file>', views.stop_sharing, name="stop_sharing"),
    path('rename/<folder>', views.rename, name="rename"),
    path('cut/<file>', views.cut, name="cut"),
    path('paste', views.paste, name="paste")
]