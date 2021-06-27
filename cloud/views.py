import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.db import models
from django.http import HttpResponse
from .models import File, Folder, CustomUser, Context
from .forms import NewUserForm, FileForm, FolderForm
from django.contrib.auth import login,authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile


# Create your views here.
def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.available_space = request.POST['space']
			user.save()
			login(request, user)
			#messages.success(request, "Registration successful." )
			request.session['current_path'] = os.path.join(settings.MEDIA_ROOT, request.user.username)
			return redirect("cloud:files")
		messages.error(request, "Rejestracja nie powiodła się.")
	form = NewUserForm
	context = get_context()
	context["register_form"] = form
	return render (request=request, template_name="cloud/register.html", context=context)

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)

			if user is not None:
				login(request, user)
				#messages.info(request, f"You are now logged in as {username}.")
				user = request.user
				#current_path = Folder.objects.get(user = user)
				#current_path = "cloud/files/files/{0}".format(user.username)
				request.session['current_path'] = os.path.join(settings.MEDIA_ROOT, request.user.username)
				return redirect ('cloud:files')
			else:
				messages.error(request,"Niepoprawna nazwa użytkownika lub hasło.")
		else:
			messages.error(request,"Niepoprawna nazwa użytkownika lub hasło.")
	form = AuthenticationForm()
	context = get_context()
	context["login_form"] = form
	return render(request=request, template_name="cloud/login.html", context=context)

def logout_request(request):
	logout(request)
	#messages.success(request, "You have successfully logged out.")
	return redirect('cloud:index')

def files(request):
	if request.user.is_authenticated:
		#files_list = File.objects.filter(user = request.user)
		path = request.session.get('current_path')
		current_folder = Folder.objects.get(path = path)
		#files_list, directory_list = prepare_file_list(os.listdir(path))
		files_list=[]

		for file in File.objects.all():
			if file.user == request.user:
				if file.folder.path == request.session['current_path']:
					files_list.append(file)

		folder_list = []

		for folder in Folder.objects.all():
			if folder.user == request.user:
				if folder.superior_path == request.session['current_path']:
					folder_list.append(folder)

		context = get_context()
		context['files_list']=files_list
		context['username']=request.user.username
		context['directory_list']:folder_list
		context['is_root']=current_folder.is_root
		context['directory_list'] = folder_list
		context['available_space'] = request.user.get_available_space()
		context['used_space_percent'] = request.user.get_used_percent()

		return render(request, 'cloud/files.html',context)
	else:
		return redirect('cloud:index')



def go_to_folder(request, folder):
	return redirect('cloud:index')

def index(request):
	context = get_context()
	return render(request, 'cloud/index.html', context)

def logout_view(request):
	logout(request)
	return render('cloud:index')

def profile_mail(request,username):
	u = User.object.get(username = username)

def upload(request):
	if request.user.is_authenticated:
		username = request.user.username
		if request.method == 'POST':
			form = FileForm(request.POST, request.FILES)
			if form.is_valid():
				if request.user.update_used_space(request.FILES['file'].size):
					uploadedFile = form.save(commit=False)
					uploadedFile.user = request.user
					uploadedFile.size = request.FILES['file'].size
					current_folder = Folder.objects.get(path = request.session['current_path'])
					uploadedFile.folder = current_folder
					uploadedFile.name = request.FILES['file'].name
					uploadedFile.is_shared = False
					uploadedFile.save()
					context = get_context()
					context["form"] = FileForm()
					context["uploaded_file_url"] = uploadedFile.file.url
					context["username"]=username
					return redirect('cloud:files')
					#return render(request, 'cloud/files.html', context)
				else:
					form = FileForm()
					context = get_context()
					context["form"] = FileForm()
					context["too_large_file"] = True
					context['available_space'] = request.user.get_available_space()
				return render(request, 'cloud/upload.html', context)
		else:
			form = FileForm()
			context = get_context()
			context["form"] = FileForm()
			context['available_space'] = request.user.get_available_space()
		return render(request, 'cloud/upload.html', context)
	else:
		return redirect('cloud:index')

def add_folder(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			form = FolderForm(request.POST)
			if form.is_valid():
				superior_folder = Folder.objects.get(path=request.session['current_path'])
				new_path = os.path.join(superior_folder.path, request.POST['name'])
				if Folder.objects.filter(path=new_path).count() <1:
					added_folder = form.save(commit=False)
					added_folder.user = request.user
					superior_folder = Folder.objects.get(path = request.session['current_path'])
					added_folder.superior_path = superior_folder.path
					added_folder.is_root = False
					new_path = os.path.join(superior_folder.path, added_folder.name)
					added_folder.path = new_path
					added_folder.save()
					return render(request, 'cloud/add_folder.html', {
						"form": FolderForm(),
						"added_folder": added_folder.path,
					})
				form = FolderForm()
				context = get_context()
				context["form"] = form
				context["same_name"]=True
				return render(request, 'cloud/add_folder.html', context)
		else:
			form = FolderForm()
			context = get_context()
			context["form"] = form
		return render(request, 'cloud/add_folder.html', context)
	else:
		return redirect('cloud:index')

def go_to_folder(request, folder_name):
	if request.user.is_authenticated:
		new_path = os.path.join(request.session['current_path'],folder_name)
		request.session['current_path'] = new_path
		return redirect('cloud:files')
	else:
		return redirect('cloud:index')

def back_to_superior(request):
	current_folder = Folder.objects.get(path = request.session['current_path'])
	if current_folder.is_root == False:
		request.session['current_path'] = current_folder.superior_path
	return redirect('cloud:files')

def  delete_file(request, file):
	if request.user.is_authenticated:
		id_del = file
		del_file = File.objects.get(id=id_del)
		request.user.update_used_space((del_file.file.size)*-1)

		os.remove(del_file.file.path)
		File.objects.filter(id=id_del).delete()
		return redirect('cloud:files')
	else:
		return redirect('cloud:index')

def delete_folder(request, folder):
	if request.user.is_authenticated:
		del_folder = Folder.objects.get(id=folder)
		files = File.objects.all()
		folders = Folder.objects.all()
		for file in files:
			if file.user == request.user:
				if file.folder == del_folder:
					request.user.update_used_space((file.file.size) * -1)
					os.remove(file.file.path)
					File.objects.get(id=file.id).delete()
		for folder in folders:
			if folder.user == request.user:
				if del_folder.path == folder.superior_path:
					delete_folder_rek(request.user,folder)
		#os.rmdir(os.path.join(settings.MEDIA_ROOT,request.user.username,del_folder.name))
		del_folder.delete()
		return redirect('cloud:files')
	else:
		return redirect('cloud:index')


def delete_folder_rek(user,del_folder):
	files = File.objects.all()
	folders = Folder.objects.all()
	for file in files:
		if file.user == user:
			if file.folder == del_folder:
				user.update_used_space((file.file.size) * -1)
				os.remove(file.file.path)
				File.objects.get(id=file.id).delete()
	for folder in folders:
		if folder.user == user:
			if del_folder.path == folder.superior_path:
				delete_folder_rek(user,folder)
	del_folder.delete()
	return

def get_context():
	context_object = Context.objects.get(id=1)
	context = {
		'main_text_index':context_object.main_text_index,
		'subtitle_index':context_object.subtitle_index,
		'footer':context_object.footer,
		'login_link':context_object.login_link,
		'logout_link':context_object.logout_link,
		'register_link':context_object.register_link,
		'welcome_user_files_view':context_object.welcome_user_files_view,
		'welcome_logged_user_link':context_object.welcome_logged_user_link,
		'go_to_your_files_button':context_object.go_to_your_files_button,
		'subtitle_files_view':context_object.subtitle_files_view,
	}
	return context

def share_file(request, file):
	if request.user.is_authenticated:
		File.objects.filter(id = file).update(is_shared = True)
		link = f"167.99.130.228/share/{file}"
		context = get_context()
		context['id_file'] = file
		context["shared_link"] = link

		return render(request, 'cloud/share_file.html', context)
	else:
		return redirect('cloud:index')

def share(request, file):
	shared_file = File.objects.get(id=file)
	if shared_file.is_shared:
		context = get_context()
		context['shared_file'] = shared_file
		if shared_file.file.size < 1024*1024:
			size= round(shared_file.file.size/1024,2)
			#
			context['shared_file_size'] = f"{size}KB"
		else:
			size = round(shared_file.file.size / 1024*1024,2)
			context['shared_file_size'] = f"{size}MB"
		return render(request, 'cloud/share.html', context)
	else:
		return redirect('cloud:index')

def stop_sharing(request,file):
	File.objects.filter(id = file).update(is_shared = False)
	return redirect('cloud:files')

def rename(request, folder):
	if request.user.is_authenticated:
		if request.method == "POST":
			tmp_folder = Folder.objects.get(id=folder)
			new_path = os.path.join(tmp_folder.superior_path, request.POST['new_name'])
			if Folder.objects.filter(path = new_path).count()<1:
				Folder.objects.filter(id=folder).update(name = request.POST['new_name'])
				Folder.objects.filter(id=folder).update(path = new_path)
			return redirect('cloud:files')

		else:
			return redirect('cloud:files')
	else:
		return redirect('cloud:index')

def cut(request, file):
	if request.user.is_authenticated:
		request.session['clipboard'] = file
		request.session['type_of_paste'] = "cut"
		return redirect('cloud:files')
	else:
		return redirect('cloud:index')

def paste(request):
	if request.user.is_authenticated:
		if request.session['clipboard']!=None:
			if request.session['type_of_paste'] == "cut":
				File.objects.filter(id = request.session['clipboard']).update(folder = Folder.objects.get(path = request.session['current_path']))
				request.session['clipboard']=None

		return redirect('cloud:files')
	else:
		return redirect('cloud:index')